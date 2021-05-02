from sqlalchemy import Integer, Column, String, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()
engine = create_engine('sqlite+pysqlite:///app.db', echo=True, future=True)
session = Session(engine)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    chips_url = Column(String(50))

    servers = relationship("Server", back_populates="game")
    ads = relationship("Ad", back_populates="game")

    def __repr__(self):
        return f"Game(id={self.id!r}, name={self.name!r})"


class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    game_id = Column(Integer, ForeignKey('game.id'))
    name = Column(String(50))

    game = relationship("Game", back_populates="servers")
    ads = relationship("Ad", back_populates="server")

    def __repr__(self):
        return f"Server(game_id={self.game_id!r}, name={self.name!r})"


class Ad(Base):
    __tablename__ = 'ad'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    server_id = Column(Integer, ForeignKey('server.server_id'))
    seller = Column(String(50))
    side = Column(Integer)
    price = Column(Integer)
    amount = Column(Integer)
    online = Column(Boolean)

    game = relationship("Game", back_populates="ads")
    server = relationship("Server", back_populates="ads")

    def __repr__(self):
        return f"Ad(id={self.id!r}, seller={self.seller!r}, side={self.side!r}, price={self.price!r}," \
               f" amount={self.amount!r}), online={self.online!r}"


Base.metadata.create_all(engine)
