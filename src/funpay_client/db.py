from typing import List

from sqlalchemy import select, delete
from sqlalchemy.orm import sessionmaker

from funpay_client.models import engine, Game, Server, Ad

Session = sessionmaker(engine, future=True)
session = Session()


def check_records_filled(table: str, related: tuple = None, session: Session = session) -> bool:
    stmt = f'select * from {table} where {related[0]}={related[1]}' if related else f'select * from {table}'
    result = session.execute(stmt).first()
    if not result:
        return False
    return True


def write_bulk(type_, list_: List[dict], session: Session = session) -> None:
    if type_ == 'game':
        objects = [Game(**el) for el in list_]
    elif type_ == 'server':
        objects = [Server(**el) for el in list_]
    elif type_ == 'ad':
        objects = [Ad(**el) for el in list_]
    else:
        raise ValueError
    session.bulk_save_objects(objects)


def get_game_by_name(name: str, session: Session = session) -> Game:
    stmt = select(Game).where(Game.name == name)
    return session.execute(stmt).one()[0]


def get_server_by_name(name: str, game_id: int, session: Session = session) -> Server:
    stmt = select(Server).filter_by(name=name, game_id=game_id)
    return session.execute(stmt).one()[0]


def get_ads_by_server(server_id: int, session: Session = session) -> List[Ad]:
    stmt = select(Ad).filter_by(server_id=server_id)
    return session.execute(stmt).all()


def get_ads_for(user_name: str, game_id: int = None, session: Session = session) -> List[Ad]:
    if game_id:
        stmt = select(Ad).filter_by(game_id=game_id, seller=user_name)
    else:
        stmt = select(Ad).filter_by(seller=user_name)
    return session.execute(stmt).all()


def drop_old_ads(game_id: int, session: Session = session) -> None:
    stmt = delete(Ad).where(Ad.game_id == game_id)
    session.execute(stmt)
    session.commit()
