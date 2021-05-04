import parser
import db
import cli


def update_ads(game):
    db.drop_old_ads(game.id)
    ads = parser.get_ads_for(game)
    db.write_bulk('ad', ads)


def main():
    args = cli.parse_args()
    if not db.check_records_filled('Game'):
        games = parser.get_games()
        db.write_bulk('game', games)
    game = db.get_game_by_name(args.game)
    if not db.check_records_filled('Server', ('game_id', game.id)):
        servers = parser.get_servers_for(game)
        db.write_bulk('server', servers)
    server = db.get_server_by_name(args.server, game.id)
    update_ads(game)

    print(db.get_ads_by_server(server.id))


if __name__ == "__main__":
    main()
