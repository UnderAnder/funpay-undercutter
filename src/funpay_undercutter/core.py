from statistics import mean
from typing import Optional

from funpay_undercutter import db, parser
from funpay_undercutter.models import Offer, Game


def check_games() -> None:
    if not db.check_records_filled('Game'):
        games = parser.get_games()
        db.write_bulk('game', games)


def check_servers(game: Game) -> None:
    if not db.check_records_filled('Server', ('game_id', game.id)):
        servers = parser.get_servers_for(game)
        db.write_bulk('server', servers)


def set_offers_best_price(offers: list[Offer]) -> bool:
    change_count = 0
    undercut = 10
    for offer in offers:
        curr_best_offer = db.get_best_offer_for(offer.server_id, offer.side_id)
        if not curr_best_offer:
            print(f'Skip for {offer}:', 'The best offer not found! Please set the price manually', sep='\n')
            continue
        if offer is curr_best_offer:
            print(f'Skip for {offer}:', 'Already the best offer', sep='\n')
            continue
        if curr_best_offer.price < min_price_rules(offer):
            print(f'Skip for {offer}:', 'The best offer is less than minimal price', sep='\n')
            continue
        offer.price = curr_best_offer.price - undercut
        change_count += 1
    print('Updated', change_count, 'offers')
    return parser.save_values_for(offers) if change_count > 0 else False


def set_best_price_all_for(game_id: int) -> bool:
    offers = my_offers_for(game_id)
    return set_offers_best_price(offers) if offers else False


def my_offers_for(game_id: int) -> Optional[list[Offer]]:
    user_name = parser.get_user_name()
    if not user_name:
        return None
    user_offers = db.get_offers_for(user_name, game_id)
    if not user_offers:
        return None
    return user_offers


def min_price_rules(offer: Offer, n: int = 5) -> int:
    off_percent = 0.9
    list_lowest = db.get_n_lowest_price_for(offer.server_id, offer.side_id, n)
    if not list_lowest:
        return 0
    min_price_avg = mean(list_lowest)
    return int(min_price_avg * off_percent)


def update_offers_for(game: Game) -> None:
    db.drop_old_offers_for(game.id)
    offers = parser.get_offers_for(game)
    db.write_bulk('offer', offers)
