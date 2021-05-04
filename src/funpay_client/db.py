from typing import Union, List

from sqlalchemy import select, delete
from sqlalchemy.orm import sessionmaker

from funpay_client.models import engine, Game, Server, Ad

Session = sessionmaker(engine, future=True)
session = Session()


def check_records_filled(table: str, related: tuple = None, session: Session = session) -> bool:
    stmt = f'select * from {table} where {related[0]}={related[1]}' if related else f'select * from {table}'
    with session as s:
        if not s.execute(stmt).first():
            return False
        return True


def write_bulk(type_, list_: List[dict]) -> None:
    if type_ == 'game':
        objects = [Game(**el) for el in list_]
    elif type_ == 'server':
        objects = [Server(**el) for el in list_]
    elif type_ == 'ad':
        objects = [Ad(**el) for el in list_]
    else:
        raise ValueError
    with Session.begin() as s:
        s.bulk_save_objects(objects)


def get_game_by_name(name: str, session: Session = session) -> Union[None, Game]:
    stmt = select(Game).where(Game.name == name)
    with session as s:
        game = s.execute(stmt).first()
        if not game:
            return None
        return game[0]


def get_server_by_name(name: str, game_id: int, session: Session = session) -> Union[None, Server]:
    stmt = select(Server).filter_by(name=name, game_id=game_id)
    with session as s:
        server = s.execute(stmt).first()
        if not server:
            return None
        return server[0]


def get_ads_by_server(server_id: int, session: Session = session) -> Union[None, List[Ad]]:
    stmt = select(Ad).filter_by(server_id=server_id)
    with session as s:
        ads = s.execute(stmt).all()
        if not ads:
            return None
        return ads


def drop_old_ads(game_id: int, session: Session = session) -> None:
    stmt = delete(Ad).where(Ad.game_id == game_id)
    with session as s:
        s.execute(stmt)
