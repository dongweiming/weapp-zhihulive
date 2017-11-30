from sqlalchemy import (
    Column, Text, Integer, create_engine, DateTime,
    SmallInteger, String)
from sqlalchemy.orm import sessionmaker
from pymysql.err import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from config import DB_URI

Base = declarative_base()
engine = create_engine(DB_URI)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


class Review(Base):
    __tablename__ = 'reviews'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    live_id = Column(String(40), index=True)
    content = Column(Text)
    score = Column(SmallInteger)
    created_at = Column(DateTime)


    @classmethod
    def create(cls, **kwargs):
        r = cls(**kwargs)
        session.add(r)
        try:
            session.commit()
        except:
            session.rollback()
        return r


Base.metadata.create_all()
