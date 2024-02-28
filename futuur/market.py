import settings
from .futuur_api import FutuurAPI
from urllib.parse import urlparse, parse_qs


class Market(FutuurAPI):
    """
    A class for interacting with the Futuur Market.

    Attributes:
        PUBLIC_KEY (str): The public API key for authentication.
        PRIVATE_KEY (str): The private API key for authentication.
        base_url (str): The base URL for the API endpoints.

    Methods:
        __init__(): Initializes the FutuurAPI instance.
        build_signature(params: dict) -> dict: Builds the HMAC signature for the API request.
        build_headers(params: dict) -> dict: Builds the headers for the API request.
        call_api(endpoint: str, params: dict) -> dict: Makes a GET request to the API endpoint.

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
            Add more markets from the Futuur API into the instance.
        """
        parsed_url = urlparse(self.pagination.get('next'))
        query_string = parsed_url.query
        query_dict = parse_qs(query_string)
        params = {k: v[0] if len(v) == 1 else v for k, v in query_dict.items()}
        response = self.call_api('markets/', params=params)
        self.pagination = response.get('pagination')
        self.markets += response.get('results')
