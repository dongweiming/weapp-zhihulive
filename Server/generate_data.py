from sqlalchemy import func

from models.live import *
from models.utils import execute
from models.review import Review, session

s = Live.search()
s.aggs.bucket('tags', A('terms', field='tags'))
rs = execute(s.execute())
tags = [tag['key']for tag in rs.aggregations.tags.buckets]

s = Live.search()
s = s.filter('range', feedback_count={
    'gte': 30,
})
s = s.sort('-score').extra(**{'from':0, 'size': 100})
rs = execute(s.execute())

def print_result(rs):
    for r in rs:
        if r.feedback_score < 4:
            continue
        r.score = '{0:.4f}'.format(r.feedback_score)
        r.url = 'https://www.zhihu.com/lives/{}'.format(r.id)
        score_map = dict(session.query(Review.score, func.count(
            Review.score)).group_by(Review.score).filter_by(live_id=r.id).all())
        length = sum(score_map.values())
        high_pencent = float('{0:.2f}'.format((score_map.get(4, 0) +
                                               score_map.get(5, 0)) * 100 / length))
        mid_pencent = float('{0:.2f}'.format(score_map.get(3, 0) * 100 / length))
        low_pencent = float('{0:.2f}'.format(100 - high_pencent - mid_pencent))
        if low_pencent < 0.01:
            low_pencent = 0
        print('标题: {0.subject:<18} 分数: {0.score:<6} 评价人数：{0.feedback_count:<4} 参与人数: {0.seats_taken:<5}  '
              '单价：{0.amount:<5} 链接: {0.url}'.format(r))
        print('好评: {}%\t中评：{}%\t差评：{}%'.format(high_pencent, mid_pencent,
                                                       low_pencent))

print_result(rs)

for tag in tags:
    s = Live.search()
    s = s.query(Q('term', tags=tag))
    sf = SF('script_score', script={
        'lang': 'painless',
        'inline': ("Math.log10(doc['seats_taken'].value * doc['amount'].value"
                   " * doc['feedback_count'].value) * "
                   "doc['feedback_score'].value")
    })
    s = s.query(Q('function_score', functions=[sf]))
    s = s.extra(**{'from':0, 'size': 30})
    rs = execute(s.execute())
    print('-' * 30)
    print('## {}'.format(tag))
    print_result(rs)
