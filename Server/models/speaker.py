from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, create_engine, SmallInteger, desc as _desc,
    DateTime)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DB_URI, SUGGEST_USER_LIMIT, PEOPLE_URL, LIVE_USER_URL

Base = declarative_base()
engine = create_engine(DB_URI)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    # 表的结构:
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    speaker_id = Column(String(40), index=True, unique=True)
    name = Column(String(40), index=True, nullable=False)
    gender = Column(SmallInteger, default=2)
    headline = Column(String(200))
    avatar_url = Column(String(100), nullable=False)
    bio = Column(String(500))
    description = Column(String(1000))
    live_count = Column(Integer, default=0)
    updated_time = Column(DateTime, default=datetime.now)

    @classmethod
    def add(cls, **kwargs):
        speaker_id = kwargs.get('speaker_id', None)
        r = None
        if id is not None:
            q = session.query(cls).filter_by(speaker_id=speaker_id)
            r = q.first()
            if r:
                q.update(kwargs)

        if r is None:
            r = cls(**kwargs)
            session.add(r)
        try:
            session.commit()
        except Exception as e:
            print('Error: {}'.format(e))
            session.rollback()
        else:
            return r

    def incr_live_count(self):
        self.live_count += 1
        session.commit()

    @property
    def url(self):
        return PEOPLE_URL.format(self.speaker_id)

    @property
    def lives_url(self):
        return LIVE_USER_URL.format(self.speaker_id)

    @classmethod
    def suggest(cls, q, start=0, limit=SUGGEST_USER_LIMIT):
        query = session.query(User)
        users = query.filter(User.name.like('%{}%'.format(q))).offset(
            start).limit(limit).all()
        return [user.to_dict() for user in users]

    def to_dict(self):
        d = {c.name: getattr(self, c.name, None)
             for c in self.__table__.columns}
        d.update({
            'type': 'user',
            'url': self.url,
            'lives_url': self.lives_url
        })
        return d

    @classmethod
    def get_all(cls, order_by='id', start=0, limit=10, desc=False):
        '''
        :param order_by:  One of ``'id'``, ``'live_count'`` or
                          ``'updated_time'``
        '''
        query = session.query(User)
        order_by = getattr(User, order_by)
        if desc:
            order_by = _desc(order_by)
        users = query.order_by(order_by).offset(start).limit(limit).all()
        return [user.to_dict() for user in users]

Base.metadata.create_all()
