from typing import List

import requests
from bs4 import BeautifulSoup

import funpay_client.db as db

FUNPAY_URL = "https://funpay.ru/"


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


def get_servers_for(game: db.Game) -> List[dict]:
    result = list()
    tmp = list()
    print('Loading servers names from', game.chips_url)
    req = connect_to(game.chips_url)
    soup = BeautifulSoup(req.content, 'lxml')
    ads_table = soup.find('div', class_='tc table-hover table-clickable showcase-table tc-sortable tc-lazyload')
    ads = ads_table.find_all('a', class_='tc-item')
    for ad in ads:
        server_id = ad["data-server"]
        server_id = 0 if server_id == '*' else int(server_id)
        if server_id not in tmp:
            tmp.append(server_id)
            server_name = ad.find('div', class_='tc-server').text
            result.append({'id': server_id, 'game_id': game.id, 'name': server_name})
    return result


def get_ads_for(game: db.Game) -> List[dict]:
    print('Loading ads from', game.chips_url)
    result = list()
    req = connect_to(game.chips_url)
    soup = BeautifulSoup(req.content, 'lxml')
    ads_table = soup.find('div', class_='tc table-hover table-clickable showcase-table tc-sortable tc-lazyload')
    ads = ads_table.find_all('a', class_='tc-item')
    for ad in ads:
        server_id = ad["data-server"]
        server_id = 0 if server_id == '*' else int(server_id)
        side = ad.find('div', class_='tc-side').text
        try:
            online = bool(ad["data-online"])
        except KeyError:
            online = False
        price = ad.find('div', class_='tc-price').find('div').next_element.replace(' ', '')
        price = int(float(price) * 100)
        amount = int(ad.find('div', class_='tc-amount').next.replace(' ', ''))
        name = ad.find('div', class_='media-user-name').text
        result.append({'game_id': game.id, 'server_id': server_id, 'seller': name, 'side': side,
                       'price': price, 'amount': amount, 'online': online})
    return result


def connect_to(target: str = None, cookie: dict = None) -> requests.Response:
    session = requests.Session()
    headers = {
        'authority': 'funpay.ru',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.93 Safari/537.36',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'dnt': '1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'sec-fetch-site': 'none',
        'referer': target,
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': f'PHPSESSID={cookie["phpsessid"]}; golden_key={cookie["golden"]};' if cookie else '',
    }
    req = session.get(target, headers=headers)

    if not req:
        print(f"Unable to connect to {target}, {req.status_code}")
        exit()

    return req


def get_user_name(cookie):
    req = connect_to(FUNPAY_URL, cookie)
    soup = BeautifulSoup(req.content, 'lxml')
    user_name = soup.find('div', class_='user-link-name')
    if not user_name:
        print("Error: can't get user name, check your cookie")
    return user_name.text
