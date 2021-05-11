import argparse
from typing import Optional

from funpay_client import parser, db, models, utils, core


def get_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser(description='Funpay funpay_client')
    parse.add_argument('game', type=str, default='World of Warcraft RU, EU', nargs='?', metavar='Game name',
                       help='Name with region in double quotes. Default: "World of Warcraft RU, EU"')
    parse.add_argument('-ra', action='store_true', default=False,
                       help='Automatic undercutting of all offers for a specified game , without interactive mode')
    return parse.parse_args()


class Menu:
    def __init__(self, name: str, options: list = None, master=None, callback=None, back: bool = False):
        self.options = options if options is not None else []
        self.name = name
        self.master = master
        self.callback = callback
        self.back = back

    def __call__(self) -> None:
        print('=====', self.name, '=====')
        if self.callback:
            if isinstance(self.callback, (list, tuple)):
                self.callback[0](*self.callback[1::])
            elif callable(self.callback):
                self.callback()
            else:
                raise ValueError('Callback is not a list, tuple or callable')
        if self.options:
            print('\n'.join(f"{(i + 1) % len(self.options)}. {option.name}" for i, option in enumerate(self.options)))
            allowed = tuple(str(i) for i in range(len(self.options)))
            user_choice = check_input(proper_values=allowed, back=self.back)
            if not user_choice:
                self()
            self.options[int(user_choice) - 1]()
        if self.master:
            self.master()

    def add_options(self, *options):
        self.options += options


def main_menu() -> None:
    args = get_args()
    game = db.get_game_by_name(args.game)
    menu = Menu(game.name, back=True)
    main_update_offers = Menu('Update data', master=menu, callback=(core.update_offers_for, game))
    main_set_lowest = Menu('Undercut all offers', master=menu,
                           callback=(core.set_best_price_all_for, game.id))
    main_change_menu = Menu('Change offer', master=menu, callback=(change_menu, game))
    main_exit = Menu('Exit', callback=utils.exit_)

    menu.add_options(main_update_offers, main_set_lowest, main_change_menu, main_exit)
    menu()


def change_menu(game) -> None:
    offer = select_offer(game)
    if not offer:
        return None
    menu = Menu('Change offer', master=main_menu, back=True)
    change_set_lowest = Menu('Undercut', master=menu,
                             callback=(core.set_offers_best_price, [offer]))
    change_edit = Menu('Edit offer', callback=(edit_offer, offer))
    menu_back = Menu('Back', callback=main_menu)

    menu.add_options(change_set_lowest, change_edit, menu_back)
    menu()
    return None


def select_offer(game) -> Optional[models.Offer]:
    user_offers = core.my_offers_for(game.id)
    if not user_offers:
        print('No active offers found')
        return None
    print('\n'.join(f'{i}. {offer}' for i, offer in enumerate(user_offers, start=1)))
    allowed = tuple(str(i) for i in range(1, len(user_offers) + 1))
    user_choice = check_input('Select one: ', proper_values=allowed)
    return user_offers[int(user_choice) - 1]


def edit_offer(offer: models.Offer) -> bool:
    price = input('Price with commission (leave blank to save old price): ')
    if utils.isfloat(price):
        save_price = int(float(price) * 1000)
        offer.price = save_price
        print('Price without commission:', utils.price_without_commission(save_price))
    else:
        print('Wrong value, should be like 1.23' if price else f'Price: {offer.price / 1000}')
    amount = input('Amount (leave blank to save old price): ')
    if utils.isint(amount):
        offer.amount = int(amount)
    else:
        print('Wrong value, should be like 55000' if amount else f'Amount: {offer.amount}')
    return parser.save_values_for([offer]) if any((price, amount)) else False


def check_input(*args, proper_values: tuple, back: bool = False, **kwargs) -> Optional[str]:
    while True:
        raw = input(*args, **kwargs)
        if raw not in proper_values:
            print(raw, 'is not an option')
            if back:
                return None
            continue
        return raw
