import time
from typing import List
from urllib.parse import urlencode
import requests
import json
class ManifoldAPI:
    """
    A class for interacting with the Manifold API. It is implemented as a singleton, so we only ever have one instance of the class.

    Attributes:
        base_url (str): The base URL for the API endpoints.

    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the FutuurAPI instance.
        """
        self.base_url = 'https://api.manifold.markets/v0/'


    def call_api(self, endpoint: str, params: dict = None, payload: dict = None, method: str = 'GET') -> dict:

        url = self.base_url + endpoint

        url_params = '?' + urlencode(params) if params else ''

        request_kwargs = {
            'method': method,
            'url': url + url_params,
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
        

    def get_market_by_id(self, market_id="CBzyMJCDvhxzPrtmtIYV") -> dict:
        """
        Fetches the details of a specific market on the Manifold platform.

        Args:
            market_id (str): The ID of the market to fetch.

        Returns:
            dict: A dictionary containing the details of the specified market.
        """
        return self.call_api(f'market/{market_id}/', method='GET')
    

    def get_market_by_slug(self, slug="which-party-will-win-the-2024-us-pr-f4158bf9278a") -> dict:
        """
        Fetches the details of a specific market on the Manifold platform.

        Args:
            slug (str): The slug of the market to fetch.

        Returns:
            dict: A dictionary containing the details of the specified market.
        """
        return self.call_api(f'slug/{slug}/', method='GET')
    
    def list_all_markets(self):
        pass

    def _get_markets(
        self, limit: int = 500, before: str = None
    ) -> List[dict]:
        """Get a list of markets (not including comments or bets).
        [API reference](https://docs.manifold.markets/api#get-v0markets)


        Args:
            limit: Number of markets to fetch. Max 500.
            before: ID of a market to fetch markets before.

        Returns:
            The list of markets as raw JSON.
        """
        params = {"limit": limit}
        if before is not None:
            params["before"] = before
        resp = self.call_api('markets/', params=params, method='GET')
        return resp

    
    def list_markets(self, limit=500, before=None):
        params = {k: v for k, v in locals().items() if v is not None and v != '' and k != 'self'}

        res =  self.call_api('markets/', params=params, method='GET')

        return res
    
    def _get_all_markets(self, after: int = 0, total_limit: int = 20_000) -> List[dict]:
        """Underlying API call for `get_all_markets`.

        Returns:
            Markets as raw JSON.
        """
        markets= []
        i = None
        while True:
            num_to_get = min(total_limit - len(markets), 500)
            if num_to_get <= 0:
                break
            new_markets = [
                x
                for x in self._get_markets(before=i, limit=num_to_get)
                if x["createdTime"] > after
            ]
            markets.extend(new_markets)
            print(f"Fetched {len(markets)} markets.")
            print("Markets: ", len(markets))
            #todo remove this line
            if len(new_markets) < 500:
                break
            else:
                i = markets[-1]["id"]

        assert len(markets) == len({m["id"] for m in markets})
        return markets


    def get_all_markets(self, after: int = 0, total_limit = 20_000) -> dict:
        markets = self._get_all_markets(after=after, total_limit = 20_000)

        sorted_markets = sorted(markets, key=lambda x: x['volume24Hours'], reverse=True)
        
        with open('mani_data.json', 'w', encoding='utf-8') as f:
            json.dump(sorted_markets, f, ensure_ascii=False, indent=4)
        return sorted_markets

