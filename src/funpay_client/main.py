from funpay_client import cli
from funpay_client import db
from funpay_client import models
from funpay_client import parser


def update_ads(game: models.Game) -> None:
    db.drop_old_ads_for(game.id)
    ads = parser.get_ads_for(game)
    db.write_bulk('ad', ads)


def price_without_commission(price) -> float:
    return round((price - price * 0.19), 3)


def main():
    cookie = cli.parse_cookie()
    args = cli.parse_args()
    if not db.check_records_filled('Game'):
        games = parser.get_games()
        db.write_bulk('game', games)
    game = db.get_game_by_name(args.game)
    if not db.check_records_filled('Server', ('game_id', game.id)):
        servers = parser.get_servers_for(game)
        db.write_bulk('server', servers)


if __name__ == "__main__":
    main()
