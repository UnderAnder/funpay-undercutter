from typing import List

from sqlalchemy import select, delete
from sqlalchemy.orm import sessionmaker

from funpay_client.models import engine, Game, Server, Offer

Session = sessionmaker(engine, future=True)
sess = Session()


def check_records_filled(table: str, related: tuple = None, session: Session = sess) -> bool:
    stmt = f'select * from {table} where {related[0]}={related[1]}' if related else f'select * from {table}'
    result = session.execute(stmt).first()
    if not result:
        return False
    return True


def write_bulk(type_, list_: List[dict], session: Session = sess) -> None:
    if type_ == 'game':
        objects = [Game(**el) for el in list_]
    elif type_ == 'server':
        objects = [Server(**el) for el in list_]
    elif type_ == 'offer':
        objects = [Offer(**el) for el in list_]
    else:
        raise ValueError
    session.bulk_save_objects(objects)
    session.commit()


def get_game_by_name(name: str, session: Session = sess) -> Game:
    stmt = select(Game).where(Game.name == name)
    return session.execute(stmt).scalar()


def get_server_by_name(name: str, game_id: int, session: Session = sess) -> Server:
    stmt = select(Server).filter_by(name=name, game_id=game_id)
    return session.execute(stmt).scalar()


def get_offers_by_server(server_id: int, session: Session = sess) -> List[Offer]:
    stmt = select(Offer).filter_by(server_id=server_id)
    return session.execute(stmt).scalars().all()


def get_offers_for(user_name: str, game_id: int = None, session: Session = sess) -> List[Offer]:
    if game_id:
        stmt = select(Offer).filter_by(game_id=game_id, seller_name=user_name)
    else:
        stmt = select(Offer).filter_by(seller_name=user_name)
    return session.execute(stmt).scalars().all()


def drop_old_offers_for(game_id: int, session: Session = sess) -> None:
    stmt = delete(Offer).where(Offer.game_id == game_id)
    session.execute(stmt)
    session.commit()


def get_best_offer_for(server_id: int, side_id: int) -> Offer:
    stmt = select(Offer).filter_by(server_id=server_id, side_id=side_id, online=1).order_by(Offer.price)
    return sess.execute(stmt).first()[0]
