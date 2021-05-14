from sqlalchemy import Integer, Column, String, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
engine = create_engine('sqlite+pysqlite:///../../app.db', future=True)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    chips_url = Column(String(50))

    servers = relationship("Server", back_populates="game")
    offers = relationship("Offer", back_populates="game")

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
    offers = relationship("Offer", back_populates="server")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Server):
            return self.id == other.id
        return NotImplemented

    def __repr__(self):
        return f"Server(id={self.id!r}, game_id={self.game_id!r}, name={self.name!r})"


class Offer(Base):
    __tablename__ = 'offer'
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer)
    seller_name = Column(String(50))
    chip_id = Column(Integer)
    game_id = Column(Integer, ForeignKey('game.id'))
    server_id = Column(Integer, ForeignKey('server.id'))
    side_name = Column(String(30))
    side_id = Column(Integer)
    price = Column(Integer)
    amount = Column(Integer)
    online = Column(Boolean)

    game = relationship("Game", back_populates="offers")
    server = relationship("Server", back_populates="offers")

    def _key(self):
        return self.server_id, self.seller_id, self.side_id

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, Offer):
            return self._key() == other._key()
        return NotImplemented

    def __repr__(self):
        return f"Offer(server_id={self.server_id!r}, seller_name={self.seller_name!r}, side={self.side_name!r}," \
               f"price={self.price!r}, amount={self.amount!r}, online={self.online!r})"

    def __str__(self):
        return f'{self.seller_name: <18} {round(float(self.price) / 1000, 3): <5}₽ {self.amount: <10} ' \
               f'{self.server.name: <20} {self.side_name: <8} {self.game.name: <8}'

    def price_for_save(self, commission: float) -> int:
        return (self.price - self.price * commission / 100)/1000


Base.metadata.create_all(engine)
