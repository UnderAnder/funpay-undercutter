from typing import Union

from sqlalchemy import Integer, Column, String, Boolean, create_engine, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite+pysqlite:///app.db', echo=True, future=True)
Session = sessionmaker(engine, future=True)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    chips_url = Column(String(50))

    servers = relationship("Server", back_populates="game")
    ads = relationship("Ad", back_populates="game")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Game):
            return self.id == other.id
        return NotImplemented

    def __repr__(self):
        return f"Game(id={self.id!r}, name={self.name!r}, chips_url={self.chips_url!r})"


class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    name = Column(String(50))

    game = relationship("Game", back_populates="servers")
    ads = relationship("Ad", back_populates="server")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Server):
            return self.id == other.id
        return NotImplemented

    def __repr__(self):
        return f"Server(id={self.id!r}, game_id={self.game_id!r}, name={self.name!r})"


class Ad(Base):
    __tablename__ = 'ad'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    server_id = Column(Integer, ForeignKey('server.id'))
    seller = Column(String(50))
    side = Column(Integer)
    price = Column(Integer)
    amount = Column(Integer)
    online = Column(Boolean)

    game = relationship("Game", back_populates="ads")
    server = relationship("Server", back_populates="ads")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Ad):
            return self.id == other.id
        return NotImplemented

    def __repr__(self):
        return f"Ad(id={self.id!r}, seller={self.seller!r}, side={self.side!r}, price={self.price!r}," \
               f" amount={self.amount!r}), online={self.online!r}"


Base.metadata.create_all(engine)


def check_table_fill(table: str, related: tuple = None) -> bool:
    stmt = f'select * from {table} where {related[0]}={related[1]}' if related else f'select * from {table}'
    with Session() as s:
        if not s.execute(stmt).first():
            return False
        return True


def get_game_by_name(name: str) -> Union[bool, Game]:
    stmt = select(Game).where(Game.name == name)
    with Session() as s:
        game = s.execute(stmt).first()
        if not game:
            return False
        return game[0]


def get_server_by_name(name: str, game_id: int) -> Union[bool, Game]:
    stmt = select(Server).filter_by(name=name, game_id=game_id)
    with Session() as s:
        server = s.execute(stmt).first()
        if not server:
            return False
        return server[0]
