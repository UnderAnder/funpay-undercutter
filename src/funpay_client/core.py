def price_without_commission(price: int) -> int:
    return int(price - price * 0.19)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False