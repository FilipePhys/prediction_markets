import settings as settings
from .futuur_api import FutuurAPI
from urllib.parse import urlparse, parse_qs


class FutuurMarket(FutuurAPI):
    """
    A class for interacting with the Futuur Market API to fetch and manage market data.

    This class inherits from FutuurAPI and provides methods specifically tailored to interacting
    with market-related endpoints of the Futuur API.

    Attributes:
        PUBLIC_KEY (str): The public API key for authentication, obtained from settings.
        PRIVATE_KEY (str): The private API key for authentication, obtained from settings.
        base_url (str): The base URL for the API endpoints, inherited from FutuurAPI.
        currency_mode (str): Determines the currency mode for market data queries ('play_money' or 'real_money').
        ordering (str): Specifies the ordering of market data results (e.g., 'relevance').
        hide_my_bets (bool): Flag to hide the user's bets in the query results.
        market_request (dict): The initial market data fetched from the API.
        pagination (dict): Contains pagination information for fetching additional market data.
        markets (list): A list of market entries fetched from the API.

    Methods:
        __init__(currency_mode="play_money", ordering="relevance", hide_my_bets=True):
            Initializes a new instance of the FutuurMarket class with default or specified settings.

        add_markets():
            Fetches additional markets based on the current pagination state and adds them to the instance's market list
    """

    def __init__(self, currency_mode="play_money", ordering="relevance",  hide_my_bets=True):
        """
        Initializes the FutuurAPI instance.

        Params:
            limit (int): The number of markets to return.
            offset (int): The number of markets to skip.
            currency_mode (str): The currency mode to use. Can be 'play_money' or 'real_money'.
            ordering (str): The ordering to use. Can be 'relevance', 'popularity', 'newest', or 'oldest'.
            hide_my_bets (bool): Whether to hide the user's bets.

        Args:
            key (str): The public key for authentication.
            secret (str): The private key for authentication.
        """
        super().__init__(key=settings.FUTUUR_PUBLIC_KEY, secret=settings.FUTUUR_PRIVATE_KEY)
        self.currency_mode = currency_mode
        self.ordering = ordering
        self.hide_my_bets = hide_my_bets

        self.market_request = self.get_markets(limit=40, offset=0)
        self.pagination = self.market_request.get('pagination')
        self.markets = self.market_request.get('results')

    def add_markets(self):
        """
        Fetches additional markets from the Futuur API based on the current pagination state and appends them to the
        instance's markets list.

        This method dynamically constructs the query parameters for the API request from the pagination information of
        the last fetched data. It updates the instance's market list and pagination info with the newly fetched data.
        """
        parsed_url = urlparse(self.pagination.get('next'))
        query_string = parsed_url.query
        query_dict = parse_qs(query_string)
        params = {k: v[0] if len(v) == 1 else v for k, v in query_dict.items()}
        response = self.call_api('markets/', params=params)
        self.pagination = response.get('pagination')
        self.markets += response.get('results')
