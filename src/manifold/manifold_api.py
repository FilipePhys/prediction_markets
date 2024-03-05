import requests

class ManifoldAPI:
    """
    A class for interacting with the Manifold API.

    Attributes:
        base_url (str): The base URL for the API endpoints.

    """

    def __init__(self):
        """
        Initializes the FutuurAPI instance.
        """
        self.base_url = 'https://api.manifold.markets/v0/'


    def call_api(self, endpoint: str, params: dict = None, payload: dict = None, method: str = 'GET') -> dict:

        url = self.base_url + endpoint

        request_kwargs = {
            'method': method,
            'url': url,
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
