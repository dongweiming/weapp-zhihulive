'''测试异步es是否运行正常'''
import asyncio
from elasticsearch_dsl.connections import  connections

from models.live import Live, SEARCH_FIELDS, init as live_init


s = Live.search()
es = connections.get_connection(Live._doc_type.using)


async def print_info():
    rs = await s.query('multi_match', query='python',
                       fields=SEARCH_FIELDS).execute()
    print(rs)

loop = asyncio.get_event_loop()
loop.run_until_complete(live_init())
loop.run_until_complete(print_info())
loop.close()
es.transport.close()
