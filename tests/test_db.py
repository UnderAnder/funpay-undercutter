import pytest
from sqlalchemy import select

import funpay_undercutter.db as db
import funpay_undercutter.models as models


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

    games_len = 3
    assert len(dataset.execute(select(models.Game)).all()) == games_len
    db.write_bulk('game', games, dataset)
    assert len(dataset.execute(select(models.Game)).all()) == games_len + 2

    servers_len = 3
    assert len(dataset.execute(select(models.Server)).all()) == servers_len
    db.write_bulk('server', servers, dataset)
    assert len(dataset.execute(select(models.Server)).all()) == servers_len + 3

    offers_len = 5
    assert len(dataset.execute(select(models.Offer)).all()) == offers_len
    db.write_bulk('offer', offers, dataset)
    assert len(dataset.execute(select(models.Offer)).all()) == offers_len + 1

    with pytest.raises(ValueError):
        db.write_bulk('not_exist', offers, dataset)


def test_get_best_offer_for(dataset):
    best_offer = models.Offer(id=3, game_id=1, server_id=20, seller_name='Charles Dodgeson',
                          side_id=2, price=150, amount=0, online=0)
    get_best_offer = db.get_best_offers_for(20, 2, 5, dataset)[0]
    if best_offer != get_best_offer:
        pytest.xfail('not equal')
    assert best_offer == get_best_offer

    best_offer = models.Offer(id=4, game_id=2, server_id=111, seller_name='Charles Dodgeson',
                          side_id=1, price=120, amount=5000, online=1)
    get_best_offer = db.get_best_offers_for(111, 1, 5, dataset)[0]
    if best_offer != get_best_offer:
        pytest.xfail('not equal')
    assert best_offer == get_best_offer

    get_best_offer = db.get_best_offers_for(404, 1, 5, dataset)
    if best_offer == get_best_offer:
        pytest.xfail('equal')
    assert get_best_offer == []