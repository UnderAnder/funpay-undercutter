from funpay_client import cli
from funpay_client import db
from funpay_client import parser


def main():
    args = cli.get_args()
    if not db.check_records_filled('Game'):
        games = parser.get_games()
        db.write_bulk('game', games)
    game = db.get_game_by_name(args.game)
    if not db.check_records_filled('Server', ('game_id', game.id)):
        servers = parser.get_servers_for(game)
        db.write_bulk('server', servers)

    menu = cli.main_menu()
    menu()


if __name__ == "__main__":
    main()
