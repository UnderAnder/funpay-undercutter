import argparse
import os
from typing import Optional

from funpay_client import parser, db, models


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Funpay funpay_client')
    parser.add_argument('game', type=str, default='World of Warcraft RU, EU', nargs='?',
                        metavar='Game name', help='e.g "World of Warcraft RU, EU"')
    parser.add_argument('server', type=str, default='Азурегос', nargs='?', metavar='Server name',
                        help='e.g "Silvermoon"')
    return parser.parse_args()


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
            print('\n'.join(f"{i}. {option.name}" for i, option in enumerate(self.options, start=1)))
            allowed = tuple(str(i) for i in range(1, len(self.options) + 1))
            user_choice = check_input(proper_values=allowed, back=self.back)
            if not user_choice:
                self()
            self.options[int(user_choice) - 1]()
        if self.master:
            self.master()

    def add_options(self, *options):
        self.options += options


def main_menu():
    args = get_args()
    game = db.get_game_by_name(args.game)
    menu = Menu(game.name, back=True)
    main_update_ads = Menu(f'Update data', callback=(parser.update_ads_for, game))
    main_set_lowest = Menu('Set all my lots at the lowest price', master=menu)
    main_change_menu = Menu('Change ad', master=menu, callback=(change_menu, game))
    main_new_ad = Menu('New ad', master=menu)
    main_exit = Menu('Exit', callback=exit)

    menu.add_options(main_update_ads, main_set_lowest, main_change_menu, main_new_ad, main_exit)
    return menu


def change_menu(game) -> None:
    ad = select_ad(game)
    if not ad:
        return None
    menu = Menu('Change ad', master=main_menu, back=True)
    change_set_lowest = Menu('Set ad to the lowest price', master=menu)
    change_edit = Menu('Edit ad', callback=(edit_ad, ad))
    menu_back = Menu('Back', callback=main_menu)

    menu.add_options(change_set_lowest, change_edit, menu_back)
    menu()


def select_ad(game) -> Optional[models.Ad]:
    user_name = parser.get_user_name()
    if not user_name:
        return None
    user_ads = db.get_ads_for(user_name, game.id)
    if not user_ads:
        return None
    print('\n'.join(f'{i}. {ad[0]}' for i, ad in enumerate(user_ads, start=1)))
    allowed = tuple(str(i) for i in range(1, len(user_ads) + 1))
    user_choice = check_input('Select one: ', proper_values=allowed)
    return user_ads[int(user_choice) - 1][0]


def edit_ad(ad: models.Ad):
    def price_without_commission(price) -> float:
        return round((price - price * 0.19), 3)
    price = float(input('Price with commission (leave blank to save old price): '))
    if price:
        without_commission = price_without_commission(price)
        ad.price = without_commission
        print('Price without commission:', without_commission)
    amount = int(input('Amount (leave blank to save old price): '))
    if amount:
        ad.amount = amount
    return parser.set_values_for(ad)


def setup_cookie():
    phpsessid_key = input('PHPSESSID key: ')
    golden_key = input('GOLDEN key: ')
    os.environ['FUNPAY_PHPSESSID'] = phpsessid_key
    os.environ['FUNPAY_GOLDEN'] = golden_key
    return phpsessid_key, golden_key


def get_cookie() -> Optional[dict[str, Optional[str]]]:
    # Get environment variables
    phpsessid_key = os.getenv('FUNPAY_PHPSESSID')
    golden_key = os.getenv('FUNPAY_GOLDEN')
    if not any((phpsessid_key, golden_key)):
        print('Cookie not setup, price change is impossible')
        print('You can setup persistent cookie with FUNPAY_PHPSESSID and FUNPAY_GOLDEN system variables')
        raw_input = input('Setup cookie for this session? y/n ')
        if raw_input == 'y':
            phpsessid_key, golden_key = setup_cookie()
        else:
            return None
    return {'phpsessid': phpsessid_key, 'golden': golden_key}


def check_input(*args, proper_values: tuple, back: bool = False, **kwargs) -> Optional[str]:
    while True:
        raw = input(*args, **kwargs)
        if raw not in proper_values:
            print(raw, 'is not an option')
            if back:
                return
            continue
        return raw
