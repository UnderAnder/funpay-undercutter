import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import funpay_client.db as db
import funpay_client.models as models


@pytest.fixture(scope='function')
def setup_database():
    engine = create_engine('sqlite://', future=True)
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope='function')
def dataset(setup_database):
    session = setup_database

    game1 = models.Game(id=2, name='World of Warcraft', chips_url='http://example.com/2')
    game2 = models.Game(id=1, name='Lineage 2', chips_url='http://example.com/1')
    server1 = models.Server(id=111, game_id=2, name='Азурегос')
    server2 = models.Server(id=112, game_id=2, name='Soulflayer')
    server3 = models.Server(id=20, game_id=1, name='Adena')
    ad1 = models.Ad(id=1, game_id=2, server_id=111, seller='Charles Dodgeson',
                    side=1, price=130, amount=100000, online=0)
    # server not exist
    ad2 = models.Ad(id=2, game_id=2, server_id=404, seller='Charles Dodgeson',
                    side=0, price=140, amount=100000, online=1)
    ad3 = models.Ad(id=3, game_id=1, server_id=20, seller='Charles Dodgeson',
                    side=2, price=150, amount=100000, online=0)
    # same hash as ad1
    ad4 = models.Ad(id=4, game_id=2, server_id=111, seller='Charles Dodgeson',
                    side=1, price=130, amount=100000, online=0)
    # as ad1 but other side
    ad5 = models.Ad(id=5, game_id=2, server_id=111, seller='Charles Dodgeson',
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
    assert len(dataset.execute(models.Game).all()) == 2
    assert len(dataset.execute(models.Server).all()) == 3
    assert len(dataset.execute(models.Ad).all()) == 5


def test_get_ads_by_server(dataset):
    azuregos = db.get_ads_by_server(111, dataset)
    adena = db.get_ads_by_server(112, dataset)
    not_exist = db.get_ads_by_server(1, dataset)

    assert len(azuregos) == 3
    assert len(adena) == 1
    assert not_exist is None


def test_get_server_by_name(dataset):
    azuregos = dataset.query(models.Server).where(models.Server.id == 111)[0]
    azuregos_by_name = db.get_server_by_name('Азурегос', 2, dataset)
    not_existing_server = db.get_server_by_name('NOTEX1ST', 2, dataset)

    assert azuregos is azuregos_by_name
    assert not_existing_server is None


def test_get_game_by_name(dataset):
    wow = dataset.query(models.Game).where(models.Game.id == 2)[0]
    wow_by_name = db.get_game_by_name('World of Warcraft', dataset)
    not_existing_game = db.get_game_by_name('NOTEX1ST', dataset)

    assert wow is wow_by_name
    assert not_existing_game is None


def test_check_records_filled(dataset):
    fill_table = db.check_records_filled('Ad', session=dataset)
    empty_table = db.check_records_filled('Ad', ('server_id', 113), dataset)

    assert fill_table is True
    assert empty_table is False


def test_drop_old_ads(dataset):
    azuregos = db.get_ads_by_server(111, dataset)
    assert len(azuregos) == 3

    db.drop_old_ads(2, dataset)
    azuregos = db.get_ads_by_server(111, dataset)
    assert len(azuregos) == 0


def test_get_ads_for(dataset):
    user_name = 'Charles Dodgeson'

    assert len(db.get_ads_for('not_exist', 2)) == 0
    assert len(db.get_ads_for(user_name, 2)) == 3
    assert len(db.get_ads_for(user_name)) == 4
    assert len(db.get_ads_for(user_name, 1)) == 1
    assert len(db.get_ads_for(user_name, 3)) == 0
