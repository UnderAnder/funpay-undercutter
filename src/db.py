from typing import Union, List

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from models import engine, Game, Server, Ad

Session = sessionmaker(engine, future=True)()


def check_records_filled(table: str, related: tuple = None, session: Session = Session) -> bool:
    stmt = f'select * from {table} where {related[0]}={related[1]}' if related else f'select * from {table}'
    with session as s:
        if not s.execute(stmt).first():
            return False
        return True


def get_game_by_name(name: str, session: Session = Session) -> Union[None, Game]:
    stmt = select(Game).where(Game.name == name)
    with session as s:
        game = s.execute(stmt).first()
        if not game:
            return None
        return game[0]


def get_server_by_name(name: str, game_id: int, session: Session = Session) -> Union[None, Server]:
    stmt = select(Server).filter_by(name=name, game_id=game_id)
    with session as s:
        server = s.execute(stmt).first()
        if not server:
            return None
        return server[0]


def get_ads_by_server(server_id: int, session: Session = Session) -> Union[None, List[Ad]]:
    stmt = select(Ad).filter_by(server_id=server_id)
    with session as s:
        ads = s.execute(stmt).all()
        if not ads:
            return None
        return ads
