import os
import sys
from typing import Optional

from funpay_client import db


def setup_cookie() -> tuple:
    phpsessid_key = input('PHPSESSID key: ')
    golden_key = input('GOLDEN key: ')
    os.environ['FUNPAY_PHPSESSID'] = phpsessid_key
    os.environ['FUNPAY_GOLDEN'] = golden_key
    return phpsessid_key, golden_key


def get_cookie() -> Optional[dict[str, Optional[str]]]:
    def check(phpsessid_key, golden_key):
        return bool(all((phpsessid_key, golden_key)))

    phpsessid_key = os.getenv('FUNPAY_PHPSESSID')
    golden_key = os.getenv('FUNPAY_GOLDEN')
    if check(phpsessid_key, golden_key):
        return {'phpsessid': phpsessid_key, 'golden': golden_key}

    print('Cookie not setup, price change is impossible')
    print('You can setup persistent cookie with FUNPAY_PHPSESSID and FUNPAY_GOLDEN system variables')
    raw_input = input('Setup cookie for this session? y/N: ')
    if raw_input == 'y':
        setup_cookie()
        get_cookie()
    return None


def price_without_commission(price: int) -> int:
    return int(price - price * 0.19)


def isfloat(value) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def isint(value) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def exit_(status: int = None) -> None:
    db.sess.close()
    sys.exit(status)
