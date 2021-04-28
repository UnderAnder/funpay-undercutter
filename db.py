from sqlalchemy import Integer, Column, String, Boolean, create_engine, ForeignKey
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///app.db?check_same_thread=False')
session = sessionmaker(bind=engine)()


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    game_id = Column(Integer, ForeignKey('game.id'))
    name = Column(String)


class Ad(Base):
    __tablename__ = 'ad'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    server_id = Column(Integer, ForeignKey('server.id'))
    seller = Column(String)
    side = Column(Integer)
    price = Column(Integer)
    amount = Column(Integer)
    online = Column(Boolean)
