

import json
from typing import List
from dataclasses import dataclass, field

import settings
from futuur.futuur_api import FutuurAPI
from manifold.manifold_api import ManifoldAPI
from transformers import BertTokenizer, BertModel
import torch
from scipy.spatial.distance import cosine

@dataclass
class MatchingOutcome:
    title: str
    futuur_probability: float
    manifold_probability: float

@dataclass
class MatchingMarket:
    futuur_id: int
    manifold_id: str
    total_probability: float = 1
    outcomes: List[MatchingOutcome] = field(default_factory=list)



matching_markets = [MatchingMarket(133793, "Z9uy9T4q4rAfq4sGzPA0")]



class Analizer:

    def __init__(self):
        """
        Initializes the Analizer that will determine if there are or not arbitrage oportunities
        """
        self.manifold_api = ManifoldAPI()
        self.futuur_api = FutuurAPI(settings.FUTUUR_PUBLIC_KEY, settings.FUTUUR_PRIVATE_KEY)
        self.matching_markets = self.retrieve_matching_markets_outcomes()

    def retrieve_matching_markets_outcomes(self):
        for market in matching_markets:
            futuur_market = self.futuur_api.get_market(market.futuur_id)
            mani_market =  self.manifold_api.get_market_by_id(market.manifold_id)

            mani_awnsers = mani_market.get("answers")
            futuur_outcomes = futuur_market.get("outcomes")
            total_probability = 0
            for m in mani_awnsers:
                matches = False
                for o in futuur_outcomes:
                    if m.get("text") == o.get("title"):
                        probability_mani = m['probability']
                        probability_futuur = o['price']['OOM']  # Assuming OOM odds are used
                        smaller_probability = min(probability_mani, probability_futuur)
                        total_probability += smaller_probability
                        matches = True
                        market.outcomes.append(MatchingOutcome(o.get('title'), probability_futuur, probability_mani))
                if not matches:
                    total_probability += m['probability']
            
            market.total_probability = total_probability
        
        return matching_markets
    

    def display_arbitrage(self):
        for market in self.matching_markets:
            if market.total_probability < 1:
                for outcome in market.outcomes:
                    where_bet = "Manifold" if outcome.manifold_probability < outcome.futuur_probability else "Futuur"
                    smaller_probability = min(outcome.manifold_probability, outcome.futuur_probability)
                    optimal_bet_amount = smaller_probability / market.total_probability
                    print("Bet on", where_bet, outcome.title, "with amount:", optimal_bet_amount)


    def retrieve_matching_markets(self):
        #TODO implement hugging_face semantic analyzer or something to try and identify matches. Maybe dump matches in a txt or something
        pass

    def sim(self):
            # Carregar o modelo BERT pré-treinado
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertModel.from_pretrained('bert-base-uncased')
        
        with open('futuur_data.json', 'r') as json_file:
            futuur_json = json.load(json_file)

        with open('mani_data.json', 'r') as json_file:
            mani_json = json.load(json_file)

        first = futuur_json[0]
        print(first.get('title'))
        
        def get_bert_embedding(sentence):
            inputs = tokenizer(sentence, return_tensors='pt', padding=True, truncation=True)
            outputs = model(**inputs)
            last_hidden_state = outputs.last_hidden_state
            return torch.mean(last_hidden_state, dim=1).squeeze().detach().numpy()

        # Função para calcular a similaridade entre duas frases usando embeddings BERT
        def sentence_similarity(sentence1, sentence2):
            embedding1 = get_bert_embedding(sentence1)
            embedding2 = get_bert_embedding(sentence2)
            return 1 - cosine(embedding1, embedding2)
        

        for market in mani_json[0:10]:
        

        # Função para obter embeddings de uma frase usando BERT


            # Exemplo de uso
            sentence1 = first.get('title')
            sentence2 = market.get('question')
            similarity_score = sentence_similarity(sentence1, sentence2)
            print(sentence2, similarity_score)

    