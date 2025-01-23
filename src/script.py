from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

import os
from dotenv import load_dotenv

import requests

PUBLIC_KEY = "bf088a36e7b705ab091d6c773527a08d1e0a3ee1"

PRIVATE_KEY = "589adb13800f4bfcb040326f73a658b3ec8e67db"


import hashlib
import hmac
import datetime
from collections import OrderedDict
from urllib.parse import urlencode
import requests
import json
import time
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

FUTUUR_PUBLIC_KEY = os.environ.get("FUTUUR_PUBLIC_KEY")
FUTUUR_PRIVATE_KEY = os.environ.get("FUTUUR_PRIVATE_KEY")

POLYMARKET_HOST = os.environ.get("POLYMARKET_HOST")
POLYMARKET_KEY = os.environ.get("POLYMARKET_KEY")
POLYMARKET_CHAIN_ID = os.environ.get("POLYMARKET_CHAIN_ID")


GET_MARKETS = "/markets"
BOOK = "/book"
