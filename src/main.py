from analysis.markets_analysis import analyze
import sys

import settings
from futuur.futuur_api import FutuurAPI
from manifold.manifold_api import ManifoldAPI

if __name__ == "__main__":

    args = sys.argv[1:]
    if "-U" in args:
        manifold_api = ManifoldAPI()
        manifold_api.get_all_markets()
        futuur_api = FutuurAPI(settings.FUTUUR_PUBLIC_KEY, settings.FUTUUR_PRIVATE_KEY)
        futuur_api.get_all_markets()

    analyze()
