from futuur.market import FutuurMarket
from futuur.futuur_api import FutuurAPI
from manifold.manifold_api import ManifoldAPI
import settings

def analyze():
    markets = FutuurMarket()
    for m in markets.markets:
        print(m)

    manifold_api = ManifoldAPI()
    manifold_market = manifold_api.get_market_by_slug()

    futuur_api = FutuurAPI(settings.FUTUUR_PUBLIC_KEY, settings.FUTUUR_PUBLIC_KEY)
    futuur_market = futuur_api.get_market(133793)

    print("Mani market: ", manifold_market)
    print("Futuur market: ", manifold_market)