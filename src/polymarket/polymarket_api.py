import datetime
import hashlib
import hmac
from collections import OrderedDict
import json
import time
from typing import List
from urllib.parse import urlencode

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

import requests


class PolymarketAPI:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host="https://clob.polymarket.com/", key=None, chain_id=137):

        self.HOST = "https://api.futuur.com/api/v1/"
        self.PRIVATE_KEY = key
        self.CHAIN_ID = chain_id
        self.client = ClobClient(host, key=key, chain_id=chain_id)

    def get_all_markets(self):

        # params = {'offset': offset}

        # def get(endpoint, headers=None, data=None):
        #     return request(endpoint, GET, headers, data)

        response = self.client.get_markets()

        results: List = response.get("data")
        next_cursor = response.get("next_cursor")

        count = 100
        while next_cursor and count < 3000:
            print(count)
            count += 100
            response = self.client.get_markets(next_cursor=next_cursor)
            results.extend(response.get("data"))

            time.sleep(2)

        with open("poly_data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        return results

    # TODO get all (?) markets, or most markets with reasonable liquidity
    # separate markets into categories
    # match categories via json file
    # try and match inteligently different possible bets.
