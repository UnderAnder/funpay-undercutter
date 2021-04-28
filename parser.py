import requests
from bs4 import BeautifulSoup


FUNPAY_URL = "https://funpay.ru/"


def connect_to(target: str) -> requests.Response:
    session = requests.Session()
    headers = {
    'authority': 'funpay.ru',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'dnt': '1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'sec-fetch-site': 'none',
    'referer': 'https://funpay.ru/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    req = session.get(f"https://funpay.ru/chips/2/", headers=headers)

    if not req:
        print(f"Sorry, unable connect to Funpay")
        exit()

    return req
