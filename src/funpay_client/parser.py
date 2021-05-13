import ssl
from functools import cache
from time import sleep
from typing import List, Optional

import requests
from requests import adapters
from urllib3 import poolmanager
from bs4 import BeautifulSoup
from funpay_client import utils
from funpay_client.models import Offer, Game

FUNPAY_URL = "https://funpay.ru/"
HEADERS = {
    'authority': 'funpay.ru',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/90.0.4430.93 Safari/537.36',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'dnt': '1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'sec-fetch-site': 'none',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}


# workaround for https://github.com/psf/requests/issues/4775
class TLSAdapter(adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)


session = requests.Session()
session.mount('https://', TLSAdapter())


def get_games() -> List[dict]:
    result = list()

    print(f'Get games list from {FUNPAY_URL}')
    req = connect_to(FUNPAY_URL)
    soup = BeautifulSoup(req.content, 'lxml')
    game_items = soup.find_all('div', class_='promo-game-item')
    for item in game_items:
        titles = item.find_all('div', class_='game-title')
        regions = item.find_all('button', class_='btn')
        for i, title in enumerate(titles):
            game = title.find('a')
            if game['href'].find('chips') != -1:
                game_id = title["data-id"]
                game_name = f'{game.text} {regions[i].text}' if len(regions) > 0 else game.text
                chips_url = game['href']
                result.append({'id': game_id, 'name': game_name, 'chips_url': chips_url})
    return result


def get_servers_for(game: Game) -> List[dict]:
    result = list()
    tmp = list()
    req = connect_to(game.chips_url)
    soup = BeautifulSoup(req.content, 'lxml')
    offers = soup.find_all('a', class_='tc-item')
    for offer in offers:
        server_id = offer["data-server"]
        server_id = 0 if server_id == '*' else int(server_id)
        if server_id not in tmp:
            tmp.append(server_id)
            server_name = offer.find('div', class_='tc-server').text
            result.append({'id': server_id, 'game_id': game.id, 'name': server_name})
    return result


def get_offers_for(game: Game) -> List[dict]:
    result = list()
    req = connect_to(game.chips_url)
    soup = BeautifulSoup(req.content, 'lxml')
    offers = soup.find_all('a', class_='tc-item')
    for offer in offers:
        href = offer['href'].split('=')[1].split('-')  # href like https://funpay.ru/chips/offer?id=109054-22-24-159-0
        seller_id = int(href[0])
        game_id = int(href[1])
        chip_id = int(href[2])
        server_id = int(href[3])
        side_id = int(href[4])
        try:
            side_name = offer.find('div', class_='tc-side').text
        except (KeyError, AttributeError):
            side_name = ''
        try:
            online = bool(offer['data-online'])
        except KeyError:
            online = False
        price = offer.find('div', class_='tc-price').find('div').next_element.replace(' ', '')
        price = int(float(price) * 1000)
        amount = int(offer.find('div', class_='tc-amount').next.replace(' ', ''))
        name = offer.find('div', class_='media-user-name').text
        result.append({'seller_id': seller_id, 'game_id': game_id, 'chip_id': chip_id,
                       'server_id': server_id, 'seller_name': name, 'side_id': side_id,
                       'side_name': side_name, 'price': price, 'amount': amount, 'online': online})
    return result


@cache
def get_user_name() -> Optional[str]:
    cookie = utils.get_cookie()
    if not cookie:
        return None
    req = connect_to(FUNPAY_URL, cookie)
    soup = BeautifulSoup(req.content, 'lxml')
    user_name = soup.find('div', class_='user-link-name')
    if not user_name:
        print("Error: can't get user name, check your cookie")
    return user_name.text


def calc_commission(form: BeautifulSoup) -> float:
    items = form.find_all('div', class_='tc-item')
    first_item = None
    for item in items:
        tmp = item.find('input', class_='form-control price')
        if tmp.get('value') != '':
            first_item = item
            break
    if not first_item:
        return False
    try:
        price_field = first_item.find('input', class_='form-control price')
        price = price_field.get('value')
        price_with_commission = first_item.find('span', class_='js-chip-calc-min').text.split()[0]
    except ValueError:
        return False
    commission = 100 * (float(price_with_commission) - float(price)) / abs(float(price_with_commission))
    return commission


def save_values_for(offers: list[Offer]) -> bool:
    trade_url = f'{offers[0].game.chips_url}trade'
    cookie = utils.get_cookie()
    headers = HEADERS
    headers['referer'] = trade_url
    headers['cookie'] = f'PHPSESSID={cookie["phpsessid"]}; golden_key={cookie["golden"]};'

    req = connect_to(trade_url, cookie)
    soup = BeautifulSoup(req.content, 'lxml')
    form = soup.find('form', class_='form-ajax-simple')
    commission = calc_commission(form)
    fields = form.find_all('input')
    # save previous values in form
    form_data = dict((field.get('name'), 'on' if field.has_attr('checked') else field.get('value')) for field in fields)
    for offer in offers:
        form_data[f'offers[{offer.server_id}][{offer.side_id}][active]'] = 'on'
        form_data[f'offers[{offer.server_id}][{offer.side_id}][amount]'] = offer.amount
        form_data[f'offers[{offer.server_id}][{offer.side_id}][price]'] = offer.price_without_commission(commission)/1000

    post = session.post(form['action'], data=form_data, headers=headers)
    if post:
        print('New values successfully saved')
        print(f'Funpay commission: {round(commission)}%')
    else:
        print('Something went wrong, the new values are not saved', f'status code: {post.status_code}')
    return bool(post)


def connect_to(target: str = None, cookie: dict = None) -> requests.Response:
    headers = HEADERS
    headers['referer'] = target
    headers['cookie'] = f'PHPSESSID={cookie["phpsessid"]}; golden_key={cookie["golden"]};' if cookie else ''
    tries = 5
    for n in range(tries):
        try:
            print('Get data from', target)
            req = session.get(target, headers=headers)
            req.raise_for_status()
        except requests.exceptions.RequestException as err:
            print('Connection error!', err)
            print('Retry in 10 sec')
        else:
            return req
        if n == tries - 1:
            print('Maximum number of attempts, try later')
            utils.exit_(1)
        sleep(10)
