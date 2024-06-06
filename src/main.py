from analysis.markets_analysis import analyze
from matcher.matcher import Matcher
import sys

import settings
from futuur.futuur_api import FutuurAPI
from polymarket.polymarket_api import PolymarketAPI

if __name__ == "__main__":

    args = sys.argv[1:]
    if "-U" in args:
        futuur_api = FutuurAPI(settings.FUTUUR_PUBLIC_KEY, settings.FUTUUR_PRIVATE_KEY)
        futuur_api.get_all_markets()

    poly_api = PolymarketAPI(
        settings.POLYMARKET_HOST, settings.POLYMARKET_KEY, settings.POLYMARKET_CHAIN_ID
    )
    poly_api.get_all_markets()

    # analyze()

    # matcher = Matcher()
