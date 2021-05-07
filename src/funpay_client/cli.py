import argparse
import os
from typing import Optional


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


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Funpay funpay_client')
    parser.add_argument('game', type=str, default='World of Warcraft RU, EU', nargs='?',
                        metavar='Game name', help='e.g "World of Warcraft RU, EU"')
    parser.add_argument('server', type=str, default='Азурегос', nargs='?', metavar='Server name',
                        help='e.g "Silvermoon"')
    return parser.parse_args()


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
        return raw
