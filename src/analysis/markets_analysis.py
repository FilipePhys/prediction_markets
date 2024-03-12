from futuur.market import FutuurMarket
from futuur.futuur_api import FutuurAPI
from manifold.manifold_api import ManifoldAPI
import settings
from analysis.analyzer import Analizer

def analyze():

    # here's the plan. Retrieve all manifold markets, retrieve all futuur markets. 

    # store each market in each API OBJ

    # match using hugginface
    analyzer = Analizer()

    analyzer.display_arbitrage()

    manifold_api = ManifoldAPI()

    markets = manifold_api.get_all_markets()

                

    

    



