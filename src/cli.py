import argparse
import db


def parse_args():
    parser = argparse.ArgumentParser(description='Funpay client')
    parser.add_argument('game', type=str, default='World of Warcraft RU, EU', nargs='?',
                        metavar='Game name', help='e.g "World of Warcraft RU, EU"')
    parser.add_argument('server', type=str, default='Азурегос', nargs='?', metavar='Server name',
                        help='e.g "Silvermoon"')
    return parser.parse_args()


def get_params():
    args = parse_args()
    game = db.get_game_by_name(args.game)
    server = db.get_server_by_name(args.server, game.id)
    return game, server
