import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Ad, Server, Game, Base


@pytest.fixture(scope='function')
def setup_database():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope='function')
def dataset(setup_database):
    session = setup_database

    game1 = Game(id=2, name='World of Warcraft', chips_url='http://example.com/2')
    game2 = Game(id=1, name='Lineage 2', chips_url='http://example.com/1')
    server1 = Server(id=111, game_id=2, name='Azuregos')
    server2 = Server(id=112, game_id=2, name='Soulflayer')
    server3 = Server(id=20, game_id=1, name='Adena')
    ad1 = Ad(id=1, game_id=2, server_id=111, seller='Charles Dodgeson',
             side=1, price=130, amount=100000, online=0)
    ad2 = Ad(id=2, game_id=2, server_id=112, seller='Charles Dodgeson',
             side=0, price=140, amount=100000, online=1)
    ad3 = Ad(id=3, game_id=1, server_id=20, seller='Charles Dodgeson',
             side=2, price=150, amount=100000, online=0)
    # same hash as ad1
    ad4 = Ad(id=4, game_id=2, server_id=111, seller='Charles Dodgeson',
             side=1, price=130, amount=100000, online=0)
    # other side
    ad5 = Ad(id=5, game_id=2, server_id=111, seller='Charles Dodgeson',
             side=0, price=130, amount=100000, online=0)

    session.add(game1)
    session.add(game2)
    session.add(server1)
    session.add(server2)
    session.add(server3)
    session.commit()

    game1.servers.append(server1)
    game1.servers.append(server2)
    game2.servers.append(server3)
    server1.ads.append(ad1)
    server1.ads.append(ad4)
    server1.ads.append(ad5)
    server2.ads.append(ad2)
    server3.ads.append(ad3)
    session.add(ad1)
    session.add(ad2)
    session.add(ad3)
    session.commit()

    yield session


def test_database(dataset):
    assert len(dataset.query(Game).all()) == 2
    assert len(dataset.query(Server).all()) == 3
    assert len(dataset.query(Ad).all()) == 5
