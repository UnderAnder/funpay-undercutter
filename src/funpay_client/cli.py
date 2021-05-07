import argparse
import os
from typing import Optional


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
