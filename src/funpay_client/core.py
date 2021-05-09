from funpay_client import db, parser, models


def set_offer_best_price(offer: models.Offer) -> bool:
    curr_best_offer = db.get_best_offer_for(offer.server_id, offer.side_id)
    offer.price = curr_best_offer.price - 10
    return parser.save_values_for([offer])
