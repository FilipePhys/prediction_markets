from dataclasses import dataclass
import time
from typing import List, Optional
from analysis.markets_analysis import analyze
from matcher.matcher import Matcher
import re
import os

import settings
from futuur.futuur_api import FutuurAPI
from polymarket.polymarket_api import PolymarketAPI
from py_clob_client.client import ClobClient
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_markets():
    abs_path = os.path.abspath("markets.json")

    try:
        with open(abs_path, "r") as file:
            data = json.load(file)
            return data

    except FileNotFoundError:
        try:
            abs_path = os.path.abspath("src/markets.json")
            with open(abs_path, "r") as file:
                data = json.load(file)
                return data

        except FileNotFoundError:

            return None


@dataclass
class PolyUrlToConditionIds:
    url: str
    condition_ids: List[str]


@dataclass
class PolyUrlToMarkets:
    url: str
    market: dict  # TODO type this out properly
    condition_id: Optional[str] = None


@dataclass
class FutuurPayloadToPolyConditions:
    futuur_payload: dict
    poly_markets: dict


@dataclass
class FutuurOutcomeToPolyOutcome:
    futuur_outcome: Optional[list[dict]]
    poly_outcome: Optional[list[dict]]


@dataclass
class FutuurToPolyMarket:
    futuur_to_poly_outcomes: Optional[list[FutuurOutcomeToPolyOutcome]]
    agg_value: float = 0.0
    futuur_question_id: int | None = None
    agg_amount_bet_on_futuur: float = 0.0
    # TODO include more info here, like agg amount bet, and etc.


@dataclass
class FutuurOutcomesToPolyOutcomes:
    futuur_to_poly_markets: Optional[list[FutuurToPolyMarket]]


# FOCUSING MOSTLY ON YESSES AND NOs ATM
def run_main():

    # TODO
    # 1. Put futuur URLs and maifold URLs on markets.json
    # 2. Iterate all URLs and get the markets
    # 3. for reach polyfold market try and get matching outcome with futuur based on a diff algorithm or something.

    poli_client = ClobClient(
        settings.POLYMARKET_HOST,
        key=settings.POLYMARKET_KEY,
        chain_id=settings.POLYMARKET_CHAIN_ID,
    )

    data = load_markets()
    print(data)
    poly_url_list = [item["poly"] for item in data]

    # PART 1: Iterate all URLs and get the markets

    poly_url_conditions_list: List[PolyUrlToConditionIds] = []

    for url in poly_url_list:
        try:
            res_poli = requests.request(method="GET", url=url)
            matches = re.findall(
                r'"conditionId":"(0x[a-fA-F0-9]{64})', res_poli.text, re.DOTALL
            )
            poly_url_conditions_list.append(
                PolyUrlToConditionIds(url=url, condition_ids=matches)
            )
        except:
            continue
        print("Sleeping, url: ", url)
        time.sleep(1)

    poly_url_market_list: List[PolyUrlToMarkets] = []

    # As of now we're only supporting poly simple markets. Some are more complicated, the ones with many choices. We're focusing on A or B type of bets. In the future we can have some code that identifies which is which and loops over multiple condition IDs if that's the case
    for poly_url_conditions in poly_url_conditions_list:
        for condition in poly_url_conditions.condition_ids:
            res = poli_client.get_market(condition_id=condition)
            poly_url_market_list.append(
                PolyUrlToMarkets(
                    url=poly_url_conditions.url, market=res, condition_id=condition
                )
            )
            print("Sleeping, cond: ", condition)
            time.sleep(1)
            break

    futuur_payload_to_poly_conditions: List[FutuurPayloadToPolyConditions] = []

    futuur_api = FutuurAPI(settings.FUTUUR_PUBLIC_KEY, settings.FUTUUR_PRIVATE_KEY)

    for poly_url_market in poly_url_market_list:

        for item in data:
            if item["poly"] == poly_url_market.url:
                res = futuur_api.get_market(item["futuur"])

                futuur_payload_to_poly_conditions.append(
                    FutuurPayloadToPolyConditions(
                        futuur_payload=res, poly_markets=poly_url_market.market
                    )
                )

                print("Sleeping, futuur_id: ", item["futuur"])
                time.sleep(1)
    print("@@@@@@@poly_url_market_list: ", futuur_payload_to_poly_conditions)

    futuur_outcomes_to_poly_outcomes = FutuurOutcomesToPolyOutcomes(
        futuur_to_poly_markets=[]
    )

    vectorizer = TfidfVectorizer()
    for match in futuur_payload_to_poly_conditions:

        market = FutuurToPolyMarket(
            futuur_to_poly_outcomes=[],
            futuur_question_id=match.futuur_payload.get("id"),
        )

        futuur_outcomes = match.futuur_payload.get("outcomes")
        poly_tokens = match.poly_markets.get("tokens")
        print("@@match.poly_markets: ", match.poly_markets)
        condition_id = match.poly_markets.get("condition_id")

        for futuur_outcome in futuur_outcomes:
            poly_outcomes = [token.get("outcome") for token in poly_tokens]

            # Create a TF-IDF Vectorizer
            vectorizer = TfidfVectorizer()

            # Combine the target string with the list of strings to compare
            texts = [futuur_outcome.get("title")] + poly_outcomes

            # Transform strings into TF-IDF vectors
            tfidf_matrix = vectorizer.fit_transform(texts)

            # Compute cosine similarity (comparing 'a' with each string in 'b')
            similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

            # Find the index of the most similar string in the list 'b'
            most_similar_index = similarity_scores[0].argmax()
            # print(
            #     f"The string most similar to '{futuur_outcome.get('title')}' is '{poly_outcomes[most_similar_index]}' at index {most_similar_index} with a cosine similarity score of {similarity_scores[0, most_similar_index]}."
            # )

            # ignore low similary. <0.1
            poly_outcome = {}
            if similarity_scores[0, most_similar_index] > 0.1:
                for token in poly_tokens:
                    if token.get("outcome") == poly_outcomes[most_similar_index]:
                        poly_outcome = {"condition_id": condition_id, **token}

            market.futuur_to_poly_outcomes.append(
                FutuurOutcomeToPolyOutcome(
                    futuur_outcome=futuur_outcome, poly_outcome=poly_outcome
                )
            )
        futuur_outcomes_to_poly_outcomes.futuur_to_poly_markets.append(market)

    for fut_to_poly in futuur_outcomes_to_poly_outcomes.futuur_to_poly_markets:
        agg_value = 0
        for single_outcome_match in fut_to_poly.futuur_to_poly_outcomes:

            agg_value += min(
                single_outcome_match.futuur_outcome.get("price").get("BTC") or 1,
                single_outcome_match.poly_outcome.get("price") or 1,
            )

        fut_to_poly.agg_value = agg_value

    # print("MATCHED OUTCOMES BY THE END: ", futuur_outcomes_to_poly_outcomes)

    limit = 50  # USDC
    print(futuur_outcomes_to_poly_outcomes)

    for fut_to_poly in futuur_outcomes_to_poly_outcomes.futuur_to_poly_markets:
        agg_amount_bet_on_futuur = 0.0
        if fut_to_poly.agg_value < 0.97:
            bets_response = futuur_api.get_betting_list(
                active=True,
                currency_mode="real_money",
                question=fut_to_poly.futuur_question_id,
            )
            for bet in bets_response.get("results"):
                active_purchases = bet.get("active_purchases")
                for active_pur in active_purchases:
                    if active_pur.get("currency") == "USDC":
                        agg_amount_bet_on_futuur += active_pur.get("amount")

            # TODO do the same for condition id to update agg amount bet

            fut_to_poly.agg_amount_bet_on_futuur = agg_amount_bet_on_futuur

            # if currency == 'USDC':
            #     print("@bet: ", bet)

    # TODO now that we have the agg price we need to iterate and hit the APIs to determine if we can make money or not. Simulate 1 dollar, then doubling. 1, 2, 4, 8....
    # TODO lastly we need to check current active bets to see if we're under the threshold to actually bet.

    # requests.request(
    #         method="GET", url=endpoint, headers=headers, json=data if data else None
    #     )


if __name__ == "__main__":
    run_main()
