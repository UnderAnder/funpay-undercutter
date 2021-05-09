from funpay_client import db, parser, models


def set_offer_best_price(offer: models.Offer) -> bool:
    curr_best_offer = db.get_best_offer_for(offer.server_id, offer.side_id)
    offer.price = curr_best_offer.price - 10
    return parser.set_values_for(offer)


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