import datetime
import hashlib
import hmac
from collections import OrderedDict
from urllib.parse import urlencode

import requests


class FutuurAPI:
    """
    A class for interacting with the Futuur API.

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

    def __init__(self, key=None, secret=None):
        """
        Initializes the FutuurAPI instance.

        Args:
            key (str): The public key for authentication.
            secret (str): The private key for authentication.
        """
        self.base_url = 'https://api.futuur.com/api/v1/'
        self.PUBLIC_KEY = key
        self.PRIVATE_KEY = secret

    def build_signature(self, params: dict) -> dict:
        """
        Builds the HMAC signature for the API request.

        Args:
            params (dict): The parameters for the API request.

        Returns:
            dict: A dictionary containing the HMAC signature and the timestamp.

        """
        if params:
            params['Key'] = self.PUBLIC_KEY
            params['Timestamp'] = int(datetime.datetime.now().timestamp())
        else:
            params = {
                'Key': self.PUBLIC_KEY,
                'Timestamp': int(datetime.datetime.now().timestamp())
            }
        # Sort the parameters in lexicographic (alphabetical) order by parameter name.
        params_to_sign = OrderedDict(sorted(list(params.items())))
        # Use urlencode to generate the URL-encoded query string of the parameters.
        params_to_sign = urlencode(params_to_sign)
        # Convert the parameters and PRIVATE_KEY into byte-strings, as required by hmac.new
        encoded_params = params_to_sign.encode('utf-8')
        encoded_private_key = self.PRIVATE_KEY.encode('utf-8')
        # Compute the HMAC using SHA-512 and convert the result into a hexadecimal string
        return {
            'hmac': hmac.new(encoded_private_key, encoded_params, hashlib.sha512).hexdigest(),
            'Timestamp': params['Timestamp']
        }

    def build_headers(self, params: dict) -> dict:
        """
        Builds the headers for the API request.

        Args:
            params (dict): The parameters for the API request.

        Returns:
            dict: A dictionary containing the headers for the request.

        """
        signature = self.build_signature(params)
        headers = {
            'Key': self.PUBLIC_KEY,
            'Timestamp': str(signature.get('Timestamp')),  # API might expect this as a string
            'HMAC': signature.get('hmac')
        }
        return headers

    def call_api(self, endpoint: str, params: dict = None, payload: dict = None, method: str = 'GET') -> dict:
        """
        Makes a request to the API endpoint.

        Args:
            endpoint (str): The API endpoint to call.
            params (dict): The parameters for the API request.
            payload (dict): The payload for the API request.
            method (str): The HTTP method to use for the request. This should be 'GET' or 'POST'.

        Returns:
            dict: The JSON response from the API.

        """
        # Encode the parameters into a URL-encoded query string without the Timestamp and HMAC parameters
        url_params = '?' + urlencode(params) if params else ''
        # Build headers for the request
        headers = self.build_headers(params or payload)
        # Build the full URL for the request
        url = self.base_url + endpoint + url_params

        request_kwargs = {
            'method': method,
            'url': url,
            'headers': headers,
        }
        if method.upper() == 'POST' and payload is not None:
            # For POST requests, include the payload as JSON in the body of the request
            request_kwargs['json'] = payload

        response = requests.request(**request_kwargs)
        try:
            return response.json()
        except ValueError:
            response = {
                "error": "Failed to parse JSON response",
                "status_code": response.status_code,
                "response": response.text
            }
            return response

    def get_markets(self, limit=40, offset=0, currency_mode="play_money", ordering="relevance",  hide_my_bets=True,
                live=None, resolved_only=False, category=None, tag=None):
        """
        Fetches the list of markets available on the Futuur platform.

        Args:
            category (int, optional): The ID of the category of markets to fetch. Default is None, fetching all categories.
            currency_mode (str): The currency mode to use. Options are 'play_money' or 'real_money'. Default is 'play_money'.
            hide_my_bets (bool): A flag indicating whether to hide the user's bets. Default is True.
            limit (int): The maximum number of markets to return per page. Default is 40.
            live (bool, optional): A flag indicating whether to fetch only live markets. Default is False.
            offset (int): The offset from which to return the results. Default is 0.
            ordering (str): The ordering of the results. Options include '', 'relevance', '-created_on',
                'bet_end_date', '-wagers_count', '-volume'. Default is '' (no specific ordering).
            resolved_only (bool): A flag indicating whether to fetch only markets that have been resolved. Default is False.
            search (str, optional): A search term to filter markets. Must be between 1 and 100 characters if provided. Default is None.
            tag (str, optional): A tag to filter the markets by. Must be between 1 and 100 characters if provided. Default is None.

        Returns:
            dict: A dictionary containing the list of markets available on the Futuur platform, along with their details.

        Notes:
            - The 'status' field in the returned market list uses specific abbreviations to indicate market status:
                'o' -> open, 's' -> stopped, 'c' -> closed (resolved), 'x' -> cancelled, 'r' -> reversed (outcome result changed).
            - Authorization via HMAC is required to access this API endpoint.
        """
        params = {k: v for k, v in locals().items() if v is not None and v != '' and k != 'self'}
        return self.call_api('markets/', params=params, method='GET')

    def get_market(self, market_id=43598):
        """
        Fetches the details of a specific market on the Futuur platform.

        Args:
            market_id (int): The ID of the market to fetch.

        Returns:
            dict: A dictionary containing the details of the specified market.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api(f'markets/{market_id}/', method='GET')

    def get_related_markets(self, market_id):
        """
        Fetches the related markets for a specified market.

        Args:
            market_id (int): The ID of the market for which to fetch related markets.

        Returns:
            dict: A dictionary containing the related markets for the specified market.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api(f'markets/{market_id}/related_markets/', method='GET')

    def follow_market(self, market_id):
        """
        Follow a market.

        Args:
            market_id (int): The ID of the market to follow.

        Returns:
            dict: A dictionary containing the response from the API.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api(f'markets/{market_id}/follow/', method='POST')

    def unfollow_market(self, market_id):
        """
        Unfollow a market.

        Args:
            market_id (int): The ID of the market to unfollow.

        Returns:
            dict: A dictionary containing the response from the API.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api(f'markets/{market_id}/unfollow/', method='POST')

    def post_comment(self, market_id, comment='Fascinating market!'):
        """
        Post a comment on a market.

        Args:
            market_id (int): The ID of the market to post a comment on.
            comment (str): The comment to post on the market. Default is 'Fascinating market!'.

        Returns:
            dict: A dictionary containing the response from the API.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        payload = {'comment': comment}
        return self.call_api(f'markets/{market_id}/comments/', payload=payload, method='POST')

    def get_betting_list(self, active=None, currency_mode="play_money", following=None, limit=40, offset=0,
                     past_bets=None, question=None, user=None):
        """
        Fetches a list of bets based on the specified filters.

        Args:
            active (bool, optional): Filter by active wagers (purchased status). None means no filter. Default is None.
            currency_mode (str): The currency mode, 'play_money' or 'real_money'. Default is 'play_money'.
            following (bool, optional): Filter by bets made by users I follow. None means no filter. Default is None.
            limit (int): Maximum number of results to return per page. Default is 40.
            offset (int): The initial index from which to return the results. Default is 0.
            past_bets (bool, optional): Filter by not active wagers (sold, won, lost, disabled). None means no filter. Default is None.
            question (int, optional): Filter by the specific question ID. None means no filter. Default is None.
            user (int, optional): Filter by the specific user ID. None means no filter. Default is None.

        Returns:
            dict or response: A dictionary containing the list of bets if the response is JSON, otherwise the raw response.

        Notes:
            - The 'status' field in the returned bets list uses specific abbreviations to indicate bet status:
                'l' -> lost, 'p' -> purchased, 's' -> sold, 'w' -> won, 'x' -> cancelled, 'd' -> disabled.
            - Authorization via HMAC is required to access this API endpoint.
        """
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.call_api('bets/', params=params, method='GET')

    def get_betting(self, bet_id):
        """
        Fetches the details of a specific bet on the Futuur platform.

        Args:
            bet_id (int): The ID of the bet to fetch.

        Returns:
            dict: A dictionary containing the details of the specified bet.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api(f'bets/{bet_id}/', method='GET')

    def sell(self, bet_id):
        """
        Sells a bet.

        Args:
            bet_id (int): The ID of the bet to sell.

        Returns:
            dict: A dictionary containing the response from the API.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api(f'bets/{bet_id}/', method='PATCH')

    def simulate_purchase(self, shares, outcome_id, currency='OOM', amount=None):
        """
        Simulates the purchase of a bet.

        Args:
            shares (int): The number of shares to purchase.
            outcome_id (int): The ID of the outcome to purchase.
            currency (str, optional): The currency to use for the purchase. Default is 'OOM'.
            amount (float, optional): The amount to purchase. Default is None.

        Returns:
            dict: A dictionary containing the response from the API.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.call_api('bets/simulate_purchase/', params=params, method='GET')

    def purchase(self, shares, outcome_id, currency='OOM', amount=None):
        """
        Purchases a bet.

        Args:
            shares (int): The number of shares to purchase.
            outcome_id (int): The ID of the outcome to purchase.
            currency (str, optional): The currency to use for the purchase. Default is 'OOM'.
            amount (float, optional): The amount to purchase. Default is None.

        Returns:
            dict: A dictionary containing the response from the API.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        payload = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.call_api('bets/', payload=payload, method='POST')

    def get_rates(self):
        """
        Fetches the rates for the OOM currency.

        Returns:
            dict: A dictionary containing the rates for the OOM currency.

        Notes:
            - Authorization via HMAC is required to access this API endpoint.
        """
        return self.call_api('bets/rates/', method='GET')
