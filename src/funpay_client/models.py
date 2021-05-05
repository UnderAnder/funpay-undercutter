from sqlalchemy import Integer, Column, String, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
engine = create_engine('sqlite+pysqlite:///../app.db', echo=True, future=True)


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
    side = Column(String(30))
    price = Column(Integer)
    amount = Column(Integer)
    online = Column(Boolean)

    game = relationship("Game", back_populates="ads")
    server = relationship("Server", back_populates="ads")

    def __key(self):
        return self.server_id, self.seller, self.side

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Ad):
            return self.__key() == other.__key()
        return NotImplemented

    def __repr__(self):
        return f"Ad(server_id={self.server_id!r}, seller={self.seller!r}, side={self.side!r}, price={self.price!r}, " \
               f"amount={self.amount!r}, online={self.online!r})"

    def __str__(self):
        return f'{self.seller: <10} {float(self.price) / 100: <4}₽ {self.amount: <8} ' \
               f'{self.server.name: <14} {self.side: <8} {self.game.name: <8}'


Base.metadata.create_all(engine)
