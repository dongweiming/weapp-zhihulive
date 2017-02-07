# coding=utf-8
from datetime import date, timedelta

from elasticsearch_dsl import (
    DocType, Date, Integer, Text, Float, Boolean, Keyword, SF, Q, A,
    Completion, Long)
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer

from config import SEARCH_FIELDS, LIVE_URL
from .speaker import User, session
from .topic import Topic

connections.create_connection(hosts=['localhost'])
gauss_sf = SF('gauss', starts_at={
    'origin': 'now', 'offset': '7d', 'scale': '10d'
})
log_sf = SF('script_score', script={
    'lang': 'painless',
    'inline': ("Math.log10(doc['seats_taken'].value * doc['amount'].value) * "
               "doc['feedback_score'].value")
})


ik_analyzer = CustomAnalyzer(
    'ik_analyzer', tokenizer='ik_max_word',
    filter=['lowercase']
)


class Live(DocType):
    id = Long()
    speaker_id = Integer()
    speaker_name = Text(analyzer='ik_max_word')
    feedback_score = Float() # 评分
    topic_names = Text(analyzer='ik_max_word')  # 话题标签名字
    seats_taken = Integer()  # 参与人数
    subject = Text(analyzer='ik_max_word')  # 标题
    amount = Float()  # 价格(RMB)
    description = Text(analyzer='ik_max_word')
    status = Boolean()  # public(True)/ended(False)
    starts_at = Date()
    outline = Text(analyzer='ik_max_word')  # Live内容
    speaker_message_count = Integer()
    tag_names = Text(analyzer='ik_max_word')
    liked_num = Integer()
    topics = Keyword()
    live_suggest = Completion(analyzer=ik_analyzer)
    cover = Text(index='not_analyzed')
    zhuanlan_url = Text(index='not_analyzed')

    @property
    def speaker(self):
        return session.query(User).get(self.speaker_id)

    @property
    def url(self):
        return LIVE_URL.format(self.id)

    class Meta:
        index = 'live102'

    def to_dict(self):
        d = self._d_.copy()
        d.update({
            'id': self._id,
            'type': 'live',
            'speaker': self.speaker.to_dict(),
            'url': self.url
        })
        return d

    @classmethod
    async def add(cls, **kwargs):
        id = kwargs.pop('id', None)
        if id is None:
            return False
        live = cls(meta={'id': int(id)}, **kwargs)
        await live.save()
        return live

    @classmethod
    async def _execute(cls, s, order_by=None):
        if order_by is not None:
            s = s.sort(order_by)
        lives = await s.execute()
        return [live.to_dict() for live in lives]

    @classmethod
    def apply_weight(cls, s, start, limit):
        return s.query(Q('function_score', functions=[gauss_sf, log_sf])).extra(
            **{'from': start, 'size': limit})

    @classmethod
    async def ik_search(cls, query, status=None, start=0, limit=10):
        s = cls.search()
        s = s.query('multi_match', query=query,
                    fields=SEARCH_FIELDS)
        if status is not None:
            s = s.query('match', status=status)
        s = cls.apply_weight(s, start, limit)
        return await cls._execute(s)

    @classmethod
    async def explore(cls, from_date=None, to_date=None, order_by=None,
                      start=0, limit=10, topic=None):
        s = cls.search()
        if topic is not None:
            s = s.query(Q('term', topic_names=topic))
        starts_at = {}
        if from_date is not None:
            starts_at['from'] = from_date
        if to_date is not None:
            starts_at['to'] = to_date
        if starts_at:
            s = s.query(Q('range', starts_at=starts_at))
        if order_by is None:
            s = cls.apply_weight(s, start, limit)
        return await cls._execute(s, order_by)

    @classmethod
    async def get_hot_weekly(cls):
        today = date.today()
        return await cls.explore(from_date=today - timedelta(days=7),
                                  to_date=today, limit=20)

    @classmethod
    async def get_hot_monthly(cls):
        today = date.today()
        return await cls.explore(from_date=today - timedelta(days=30),
                                 to_date=today, limit=50)

    @classmethod
    async def ik_search_by_speaker_id(cls, speaker_id, order_by='-starts_at'):
        s = cls.search()
        s = s.query(Q('bool', should=Q('match', speaker_id=speaker_id)))
        return await cls._execute(s, order_by)

    @classmethod
    async def get_hot_topics(cls, size=50):
        s = cls.search()
        s.aggs.bucket('topics', A('terms', field='topics', size=size))
        rs = await s.execute()
        buckets = rs.aggregations.topics.buckets
        topic_names = [r['key'] for r in buckets]
        topics = session.query(Topic).filter(Topic.name.in_(topic_names)).all()
        topics = sorted(topics, key=lambda t: topic_names.index(t.name))
        return [topic.to_dict() for topic in topics]

    @classmethod
    async def ik_suggest(cls, query, size=10):
        s = cls.search()
        s = s.suggest('live_suggestion', query, completion={
            'field': 'live_suggest', 'fuzzy': {'fuzziness': 2}, 'size': size
        })
        suggestions = await s.execute_suggest()
        matches = suggestions.live_suggestion[0].options
        ids = [match._id for match in matches]
        lives = await Live.mget(ids)
        return [live.to_dict() for live in lives]


async def init():
    await Live.init()
