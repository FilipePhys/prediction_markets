import json
import os
import settings
from futuur.futuur_api import FutuurAPI
from manifold.manifold_api import ManifoldAPI


class Matcher:
    def __init__(self):
        """
        Initializes the Analizer that will determine if there are or not arbitrage oportunities
        """
        self.manifold_api = ManifoldAPI()
        self.futuur_api = FutuurAPI(
            settings.FUTUUR_PUBLIC_KEY, settings.FUTUUR_PRIVATE_KEY
        )

    def navigate_futuur(self):
        # TODO idea is the following, have a JSON with macro categories from futuur, match with betano or bet365
        # retrieve all markets inside certain category
        # within a defined category, use some sort of algorithm to match markets

        categories = self.load_categories_from_json()
        for category in categories:

            print(category)
            futuur_category_markets = self.futuur_api.get_all_markets(
                category=category.get("futuur_id")
            )
            print(len(futuur_category_markets))
            # bet_category_markets = 0 # TODO retrieve this from any betting webiste which has categories that might match

        # for market in futuur_category_markets:
        #     print(market)
        # pass

    def load_categories_from_json(self, path="categories.json"):
        abs_path = os.path.abspath(path)
        with open(abs_path, "r") as file:
            data = json.load(file)

        return data
