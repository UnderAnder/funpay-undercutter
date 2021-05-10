from funpay_client import parser, db, cli, core, utils


def main():
    args = cli.get_args()
    if not db.check_records_filled('Game'):
        games = parser.get_games()
        db.write_bulk('game', games)
    game = db.get_game_by_name(args.game)
    if not game:
        print('Game not found, check spelling and region')
        print('Game name should be like "Lineage 2 Free", "Lineage 2 RU", '
              '"ArcheAge: Unchained", "World of Warcraft RU, EU"')
        utils.exit_()
    if not db.check_records_filled('Server', ('game_id', game.id)):
        servers = parser.get_servers_for(game)
        db.write_bulk('server', servers)
    if args.ra:
        core.update_offers_for(game)
        core.all_my_offers_best_price_for(game.id)
    else:
        cli.main_menu()


if __name__ == "__main__":
    main()
