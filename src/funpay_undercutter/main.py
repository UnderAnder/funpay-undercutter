from funpay_undercutter import db, cli, core, utils


def main():
    core.check_games()
    args = cli.get_args()
    game = db.get_game_by_name(args.game)
    if not game:
        print('Game not found, check spelling and region')
        print('Game name should be like "Lineage 2 Free", "Lineage 2 RU", '
              '"ArcheAge: Unchained", "World of Warcraft RU, EU"')
        utils.exit_()

    core.check_servers(game)

    if args.a:
        core.update_offers_for(game)
        core.set_best_price_all_for(game.id)
    else:
        cli.main_menu()


if __name__ == "__main__":
    main()
