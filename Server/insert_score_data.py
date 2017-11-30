from sqlalchemy import func

from models.live import Live
from models.review import Review, session
from models.utils import execute

s = Live.search()
s = s.extra(**{'from':0, 'size': 10000})
rs = execute(s.execute())

for r in rs:
    id = r.id
    score_map = dict(session.query(Review.score, func.count(
        Review.score)).group_by(Review.score).filter_by(live_id=id).all())
    feedback_count = sum(score_map.values())
    if feedback_count:
        feedback_score = sum(k * v for k, v in score_map.items()) / feedback_count
    else:
        feedback_score = 1
    r.score = feedback_score
    r.feedback_count = feedback_count
    execute(r.save())
    print('{} done'.format(r.id))
