import requests
from bs4 import BeautifulSoup

import db

FUNPAY_URL = "https://funpay.ru/"
session = requests.Session()


def get_ads_for(game='chips/2/'):
    print(f'Loading data from {FUNPAY_URL}{game}')
    req = connect_to(game)
    soup = BeautifulSoup(req.content, 'lxml')
    ads_table = soup.find('div', class_='tc table-hover table-clickable showcase-table tc-sortable tc-lazyload')
    ads = ads_table.find_all('a', class_='tc-item')
    for ad in ads:
        server = ad["data-server"]
        side = ad["data-side"]
        try:
            online = bool(ad["data-online"])
        except KeyError:
            online = False
        price = ad.find('div', class_='tc-price').find('div').next_element.replace(' ', '')
        price = int(float(price) * 100)
        amount = int(ad.find('div', class_='tc-amount').next.replace(' ', ''))
        name = ad.find('div', class_='media-user-name').text
        ad = db.Ad(game_id=2, server_id=server, seller=name, side=side, price=price, amount=amount, online=online)
        db.session.add(ad)
    db.session.commit()
    db.session.close()
    print('Total:', len(ads))


def populate_games():
    print(f'Get games list from {FUNPAY_URL}')
    req = connect_to()
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
                row = db.Game(id=game_id, name=game_name, chips_url=chips_url)
                db.session.add(row)
    db.session.commit()


def connect_to(target: str = None) -> requests.Response:
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
        'referer': FUNPAY_URL,
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    req = session.get(f"{FUNPAY_URL}{target if target else ''}", headers=headers)

    if not req:
        print(f"Unable to connect to {FUNPAY_URL}{target}")
        exit()

    return req