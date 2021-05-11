import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import funpay_client.models as models


@pytest.fixture(scope='function')
def setup_database():
    engine = create_engine('sqlite://', future=True)
    models.Base.metadata.create_all(engine)
    session_ = sessionmaker(bind=engine, future=True)
    session = session_()
    yield session
    session.close()


@pytest.fixture(scope='function')
def dataset(setup_database):
    session = setup_database

    game1 = models.Game(id=2, name='World of Warcraft RU/EN', chips_url='http://example.com/2')
    game2 = models.Game(id=1, name='Lineage 2', chips_url='http://example.com/1')
    game3 = models.Game(id=22, name='World of Warcraft US', chips_url='http://example.com/22')
    server1 = models.Server(id=111, game_id=2, name='Азурегос')
    server2 = models.Server(id=112, game_id=2, name='Soulflayer')
    server3 = models.Server(id=20, game_id=1, name='Adena')
    offer1 = models.Offer(id=1, game_id=2, server_id=111, seller_name='Charles Dodgeson',
                          side_id=1, price=130, amount=100000, online=0)
    # server not exist
    offer2 = models.Offer(id=2, game_id=2, server_id=404, seller_name='Charles Dodgeson',
                          side_id=0, price=140, amount=100000, online=1)
    offer3 = models.Offer(id=3, game_id=1, server_id=20, seller_name='Charles Dodgeson',
                          side_id=2, price=150, amount=100000, online=0)
    # same hash as offer1
    offer4 = models.Offer(id=4, game_id=2, server_id=111, seller_name='Charles Dodgeson',
                          side_id=1, price=130, amount=100000, online=0)
    # as offer1 but other side
    offer5 = models.Offer(id=5, game_id=2, server_id=111, seller_name='Charles Dodgeson',
                          side_id=0, price=130, amount=100000, online=0)

    session.add(game1)
    session.add(game2)
    session.add(game3)
    session.add(server1)
    session.add(server2)
    session.add(server3)
    session.commit()

    game1.servers.append(server1)
    game1.servers.append(server2)
    game2.servers.append(server3)
    server1.offers.append(offer1)
    server1.offers.append(offer4)
    server1.offers.append(offer5)
    server2.offers.append(offer2)
    server3.offers.append(offer3)
    session.add(offer1)
    session.add(offer2)
    session.add(offer3)
    session.commit()

    yield session
