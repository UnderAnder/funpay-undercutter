from funpay_client import db, parser, models


def set_offers_best_price(offers: list[models.Offer]) -> bool:
    for offer in offers:
        curr_best_offer = db.get_best_offer_for(offer.server_id, offer.side_id)
        offer.price = curr_best_offer.price - 10
    return parser.save_values_for(offers)
