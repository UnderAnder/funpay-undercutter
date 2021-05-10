from statistics import mean
from typing import Optional

from funpay_client import db, parser
from funpay_client.models import Offer


def set_offers_best_price(offers: list[Offer]) -> bool:
    undercut = 10
    for offer in offers:
        curr_best_offer = db.get_best_offer_for(offer.server_id, offer.side_id)
        if curr_best_offer.price < min_price_rules(offer):
            print(offer, 'Lowest offer less than minimal price, skipped', sep='\n')
            continue
        offer.price = curr_best_offer.price - undercut
    return parser.save_values_for(offers)


def all_my_offers_best_price_for(game_id: int) -> bool:
    offers = my_offers_for(game_id)
    return set_offers_best_price(offers) if offers else None


def my_offers_for(game_id: int) -> Optional[list[Offer]]:
    user_name = parser.get_user_name()
    if not user_name:
        return None
    user_offers = db.get_offers_for(user_name, game_id)
    if not user_offers:
        return None
    return user_offers


def min_price_rules(offer: Offer):
    min_price_avg = mean(db.get_n_lowest_price_for(offer.server_id, offer.side_id, 5))
    return int(min_price_avg * 0.9)
