import numpy as np
from tqdm import tqdm

class Card:
    largestPrime = 2
    def isPrime(n):
        for x in range(2, int(n**0.5)+1):
            if n % x == 0:
                return False
        return True
    def __init__(self, name: str, min = 0, max = 99, *flag: str):
        self.name = name
        self.min = min
        self.max = max
      
        self.flag = flag
        searching = True
        while searching:
            if Card.isPrime(Card.largestPrime):
                self.id = Card.largestPrime
                searching = False
            Card.largestPrime += 1
    def __repr__(self):
        return self.name
    def __hash__(self):
        return self.id
    
class VanguardCard(Card):
      def __init__(self, name, grade: int, unit = True, trigger = False, min=0, max=99, *flag: str):
           super().__init__(name, min, max, *flag)
           self.grade = grade
           self.isUnit = unit
           self.isTrigger = trigger

class MagicCard(Card):
      def __init__(self, name, mv: int, min=0, max=99, *flag: str):
          super().__init__(name, min, max, *flag)
          self.mv = mv

class GameEnvironment:
      def __init__(self, cards: list, deck_size: int, run_game, interpret_results):
            
            self.cards = cards
            self.maxDeckSize = deck_size
            self.run_game = run_game
            self.interpret_results = interpret_results
                 
            # Optional for certain games
            self.cache = {}

      # Generic methods, since they will differ depending on deck played
      def PlayGames(self, deck_array: tuple, number_of_games: int, debug = False):
            print(f"Playing {deck_array} for {number_of_games} games.")

            deck_dict = {card: 0 for card in self.cards}
            for i, amount in enumerate(deck_array):
                  deck_dict[self.cards[i]] = amount
            game_output = []
            for g in tqdm(range(number_of_games)):
                  result = self.run_game(deck_dict.copy(), g%2, self.cache, debug)
                  game_output.append(result)
            if self.cache:
                  print(f"Cache size: {len(self.cache.keys())}")
            return game_output
      
      def ReturnScore(self, results):
            return self.interpret_results(results)
      
      def CreateInitialDeck(self):
            amounts = []
            card: Card
            for card in self.cards:
                  amounts.append(card.min)
            budget = self.maxDeckSize - np.sum(amounts)
            while budget > 0:
                  for i, amount in enumerate(amounts):
                        if budget == 0:
                              break
                        if amount >= self.cards[i].max:
                              continue
                        amounts[i] += 1
                        budget -= 1
            return tuple(amounts)
      
      def CheckIfValid(self, deck: tuple):
            cardsInDeck = 0
            triggers = 0
            for i, amount in enumerate(deck):
                  card = self.cards[i]
                  if amount < 0:
                        return False
                  if amount < card.min:
                        return False
                  if amount > card.max:
                        return False
                  cardsInDeck += amount
                  if type(card) == VanguardCard:
                        if card.isTrigger:
                              triggers += amount
            if cardsInDeck != self.maxDeckSize:
                  return False
            if type(self.cards[0]) == VanguardCard and triggers != 16:
                 return False
            return True
      

