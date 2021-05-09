from typing import Optional

from funpay_client import db, parser, models


def set_offers_best_price(offers: list[models.Offer]) -> bool:
    for offer in offers:
        curr_best_offer = db.get_best_offer_for(offer.server_id, offer.side_id)
        offer.price = curr_best_offer.price - 10
    return parser.save_values_for(offers)


def all_my_offers_best_price_for(game_id: int) -> bool:
    offers = my_offers(game_id)
    return set_offers_best_price(offers) if offers else None


def my_offers(game_id: int) -> Optional[list[models.Offer]]:
    user_name = parser.get_user_name()
    if not user_name:
        return None
    user_offers = db.get_offers_for(user_name, game_id)
    if not user_offers:
        return None
    return user_offers
