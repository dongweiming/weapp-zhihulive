from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DB_URI, TOPIC_URL

Base = declarative_base()
engine = create_engine(DB_URI)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    avatar_url = Column(String(100))
    best_answerers_count = Column(Integer, default=0)
    best_answers_count = Column(Integer, default=0)
    name = Column(String(40), index=True, nullable=False)
    questions_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)

    @classmethod
    def add_or_update(cls, **kwargs):
        name = kwargs.get('name', None)
        if name is not None:
            q = session.query(cls).filter_by(name=name)
            r = q.first()
            if r:
                q.update(kwargs)
                return r
        try:
            r = cls(**kwargs)
            session.add(r)
            session.commit()
        except:
            session.rollback()
            raise KeyError(str(kwargs))
        else:
            return r

    @property
    def url(self):
        return TOPIC_URL.format(self.id)

    def to_dict(self):
        d = {c.name: getattr(self, c.name, None)
             for c in self.__table__.columns}
        d.update({
            'type': 'topic',
            'url': self.url
        })
        return d

Base.metadata.create_all()
