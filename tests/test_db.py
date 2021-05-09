import pytest
from sqlalchemy import create_engine, select
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


def test_database(dataset):
    assert len(dataset.execute(select(models.Game)).all()) == 3
    assert len(dataset.execute(select(models.Server)).all()) == 3
    assert len(dataset.execute(select(models.Offer)).all()) == 5


def test_get_offers_by_server(dataset):
    azuregos = db.get_offers_by_server(111, dataset)
    adena = db.get_offers_by_server(112, dataset)
    not_exist = db.get_offers_by_server(1, dataset)

    assert len(azuregos) == 3
    assert len(adena) == 1
    assert len(not_exist) == 0


def test_get_server_by_name(dataset):
    stmt = select(models.Server).filter_by(id=111)
    azuregos = dataset.execute(stmt).scalar()
    azuregos_by_name = db.get_server_by_name('Азурегос', 2, dataset)

    assert azuregos == azuregos_by_name
    assert db.get_server_by_name('NOTEX1ST', 2, dataset) is None


def test_get_game_by_name(dataset):
    stmt = select(models.Game).filter_by(id=2)
    wow = dataset.execute(stmt).scalar()
    wow_by_name = db.get_game_by_name('World of Warcraft RU/EN', dataset)

    assert wow == wow_by_name
    assert db.get_game_by_name('NOTEX1ST', dataset) is None


def test_check_records_filled(dataset):
    fill_table = db.check_records_filled('Offer', session=dataset)
    empty_table = db.check_records_filled('Offer', ('server_id', 113), dataset)

    assert fill_table is True
    assert empty_table is False


def test_drop_old_offers(dataset):
    azuregos = db.get_offers_by_server(111, dataset)
    assert len(azuregos) == 3

    db.drop_old_offers_for(2, dataset)
    azuregos = db.get_offers_by_server(111, dataset)
    assert len(azuregos) == 0


def test_get_offers_for(dataset):
    user_name = 'Charles Dodgeson'
    assert len(db.get_offers_for('not_exist', 2, dataset)) == 0
    assert len(db.get_offers_for(user_name, 2, dataset)) == 4
    assert len(db.get_offers_for(user_name, session=dataset)) == 5
    assert len(db.get_offers_for(user_name, 1, dataset)) == 1
    assert len(db.get_offers_for(user_name, 3, dataset)) == 0


def test_write_bulk(dataset):
    games = [{'id': 9, 'name': 'testgame1', 'chips_url': 'test_url'},
             {'id': 10, 'name': 'test game 2', 'chips_url': 'https://test'}]
    servers = [{'id': 5, 'game_id': 9, 'name': 'testa'},
               {'id': 6, 'game_id': 9, 'name': 'testb'},
               {'id': 7, 'game_id': 8, 'name': 'testc'}]
    offers = [{'game_id': 2, 'server_id': 5, 'seller_name': 'testname', 'side_id': 0,
            'price': 304, 'amount': 10000, 'online': False}]

    assert len(dataset.execute(select(models.Game)).all()) == 3
    db.write_bulk('game', games, dataset)
    assert len(dataset.execute(select(models.Game)).all()) == 5

    assert len(dataset.execute(select(models.Server)).all()) == 3
    db.write_bulk('server', servers, dataset)
    assert len(dataset.execute(select(models.Server)).all()) == 6

    assert len(dataset.execute(select(models.Offer)).all()) == 5
    db.write_bulk('offer', offers, dataset)
    assert len(dataset.execute(select(models.Offer)).all()) == 6

    with pytest.raises(ValueError):
        db.write_bulk('not_exist', offers, dataset)
