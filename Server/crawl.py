import os
import cgi
import time
import asyncio
import sqlite3
import logging
from asyncio import Queue
from datetime import datetime
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

import aiohttp
from elasticsearch_dsl import Q
from elasticsearch_dsl.connections import connections

from models import User, Live, Topic, session
from models.live import init as live_init
from client import ZhihuClient
from utils import flatten_live_dict
from config import SPEAKER_KEYS, LIVE_KEYS, TOPIC_KEYS, ZHUANLAN_URL

LIVE_API_URL = 'https://api.zhihu.com/lives/{type}?purchasable=0&limit=10&offset={offset}'  # noqa
ZHUANLAN_API_URL = 'https://zhuanlan.zhihu.com/api/columns/zhihulive/posts?limit=20&offset={offset}'  # noqa
TOPIC_API_URL = 'https://api.zhihu.com/topics/{}'
LIVE_TYPE = frozenset(['ongoing', 'ended'])
IMAGE_FOLDER = 'static/images/zhihu'
es = connections.get_connection(Live._doc_type.using)

if not os.path.exists(IMAGE_FOLDER):
    os.mkdir(IMAGE_FOLDER)


def get_next_url(url):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query['offset'] = int(query['offset']) + int(query['limit'])
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def gen_suggests(topics, tags, outline, username, subject):
    suggests = [{'input': item, 'weight': weight}
                for item, weight in ((topics, 10), (subject, 5), (outline, 3),
                                     (tags, 3), (username, 2)) if item]
    return suggests


class Crawler:
    def __init__(self, max_redirect=10, max_tries=4,
                 max_tasks=10, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = Queue(loop=self.loop)
        self.seen_urls = set()
        self.seen_topics = set()
        for t in LIVE_TYPE:
            for offset in range(max_tasks):
                self.add_url(LIVE_API_URL.format(type=t, offset=offset * 10))
        self.t0 = time.time()
        self.t1 = None
        self.client = ZhihuClient()
        self.headers = {}
        self.client.auth(self)
        self._session = None
        self.__stopped = {}.fromkeys(['ended', 'ongoing', 'posts'], False)

    async def check_token(self):
        async with self.session.get(
            LIVE_API_URL.format(type='ended', offset=0)) as resp:
            if resp.status == 401:
                self.client.refresh_token()

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers=self.headers, loop=self.loop)
        return self._session

    async def convert_local_image(self, pic):
        pic_name = pic.split('/')[-1]
        path = os.path.join(IMAGE_FOLDER, pic_name)
        if not os.path.exists(path):
            async with self.session.get(pic) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return path

    def close(self):
        self.session.close()

    async def parse_zhuanlan_link(self, response):
        posts = await response.json()

        if response.status == 200 and posts:
            for post in posts:
                cover = post['titleImage']
                if not cover:
                    continue
                s = Live.search()
                title = post['title']
                if '－－' in title:
                    title = title.split('－－')[1].strip()
                speaker_id = post['author']['hash']
                s = s.query(Q('match_phrase', subject=title))
                lives = await s.execute()
                for live in lives:
                    if live.speaker and live.speaker.speaker_id == speaker_id:
                        zid = post['url'].split('/')[-1]
                        cover = await self.convert_local_image(cover)
                        await live.update(
                            cover=cover, zhuanlan_url=ZHUANLAN_URL.format(zid))
            return get_next_url(response.url)

    async def parse_topic_link(self, response):
        rs = await response.json()
        if response.status == 200:
            rs['avatar_url'] = await self.convert_local_image(
                rs['avatar_url'].replace('_s', '_r'))
            Topic.add_or_update(**flatten_live_dict(rs, TOPIC_KEYS))

    async def parse_live_link(self, response):
        rs = await response.json()

        if response.status == 200:
            for live in rs['data']:
                speaker = live.pop('speaker')
                speaker_id = speaker['member']['id']
                speaker['member']['avatar_url'] = await self.convert_local_image(  # noqa
                    speaker['member']['avatar_url'])
                user = User.add(speaker_id=speaker_id,
                                **flatten_live_dict(speaker, SPEAKER_KEYS))
                live_dict = flatten_live_dict(live, LIVE_KEYS)
                topics = live_dict.pop('topics')
                for topic in topics:
                    topic_id = topic['id']
                    if topic_id not in self.seen_topics:
                        self.seen_topics.add(topic_id)
                        self.add_url(TOPIC_API_URL.format(topic_id),
                                     self.max_redirect)

                topics = [t['name'] for t in topics]
                tags = ' '.join(set(sum([(t['name'], t['short_name'])
                                         for t in live_dict.pop('tags')], ())))
                live_dict['speaker_id'] = user.id
                live_dict['speaker_name'] = user.name
                live_dict['topics'] = topics
                live_dict['topic_names'] = ' '.join(topics)
                live_dict['seats_taken'] = live_dict.pop('seats')['taken']
                live_dict['amount'] = live_dict.pop('fee')['amount'] / 100
                live_dict['status'] = live_dict['status'] == 'public'
                live_dict['tag_names'] = tags
                live_dict['starts_at'] = datetime.fromtimestamp(
                    live_dict['starts_at'])
                live_dict['live_suggest'] = gen_suggests(
                    live_dict['topic_names'], tags, live_dict['outline'],
                    user.name, live_dict['subject'])

                result = await Live.add(**live_dict)
                if result.meta['version'] == 1:
                    user.incr_live_count()

            paging = rs['paging']
            if not paging['is_end']:
                next_url = paging['next']
                return paging['next']
        else:
            print('HTTP status_code is {}'.format(response.status))

    async def fetch(self, url, max_redirect):
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                response = await self.session.get(
                    url, allow_redirects=False)
                break
            except aiohttp.ClientError as client_error:
                exception = client_error

            tries += 1
        else:
            return

        try:
            if 'api.zhihu.com' in url:
                parse_func = (self.parse_topic_link if 'topics' in url
                        else self.parse_live_link)
                next_url = await parse_func(response)
            else:
                next_url = await self.parse_zhuanlan_link(response)
            print('{} has finished'.format(url))
            if next_url is not None:
                self.add_url(next_url, max_redirect)
            else:
                for type in self.__stopped:
                    if type in url:
                        self.__stopped[type] = True
        finally:
            response.release()

    async def work(self):
        try:
            while 1:
                url, max_redirect = await self.q.get()
                if url in self.seen_urls:
                    type = url.split('/')[-1].split('?')[0]
                    if not type.isdigit() and not self.__stopped[type]:
                        self.add_url(get_next_url(url), max_redirect)
                await self.fetch(url, max_redirect)
                self.q.task_done()
                asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def add_url(self, url, max_redirect=None):
        if max_redirect is None:
            max_redirect = self.max_redirect
        if url not in self.seen_urls:
            self.seen_urls.add(url)
            self.q.put_nowait((url, max_redirect))

    def add_zhuanlan_urls(self):
        for offset in range(self.max_tasks):
            self.add_url(ZHUANLAN_API_URL.format(offset=offset * 20))

    async def crawl(self):
        await self.check_token()
        self.__workers = [asyncio.Task(self.work(), loop=self.loop)
                          for _ in range(self.max_tasks)]
        loop.call_later(5, self.add_zhuanlan_urls)
        self.t0 = time.time()
        await self.q.join()
        self.t1 = time.time()
        for w in self.__workers:
            w.cancel()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    crawler = Crawler()
    loop.run_until_complete(live_init())
    loop.run_until_complete(crawler.crawl())
    print('Finished in {:.3f} secs'.format(crawler.t1 - crawler.t0))
    crawler.close()

    loop.close()
    es.transport.close()
