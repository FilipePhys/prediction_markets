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
        return self.call_api(f'market/{market_id}/', method='GET')
