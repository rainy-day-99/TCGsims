import numpy as np
from tqdm import tqdm

class Card:
    largestPrime = 2
    def isPrime(n):
        for x in range(2, int(n**0.5)+1):
            if n % x == 0:
                return False
        return True
    def __init__(self, name: str, min = 0, max = 99):
        self.name = name
        self.min = min
        self.max = max

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
      def __init__(self, name, grade: int, unit = True, trigger = False, inRideDeck = False, min=0, max=99):
           super().__init__(name, min, max)
           self.grade = grade
           self.isUnit = unit
           self.isTrigger = trigger
           self.inRideDeck = inRideDeck

class MagicCard(Card):
      def __init__(self, name, mv: int, min=0, max=99):
          super().__init__(name, min, max)
          self.mv = mv

class DreamscapeCard(Card):
      def __init__(self, name, level: int, insight: int, character = True, verse = False, min=0, max=99):
            super().__init__(name, min, max)
            self.level = level
            self.insight = insight
            self.isCharacter = character
            self.isVerse = verse

      @property
      def value(self):
            return self.level + 1
      def discard(self):
            if not self.isCharacter:
                 return True
            threshold = 1 / (1+self.level)
            if np.random.random() < threshold:
                return False
            return True
           
class GameEnvironment:
      def __init__(self, cards: list, deck_size: int, 
                   run_game, interpret_results):
            
            self.cards = cards
            self.maxDeckSize = deck_size
            self.run_game = run_game
            self.interpret_results = interpret_results

            self.format = "Standard"
            # Optional for certain games
            self.cache = {}

      # Generic methods, since they will differ depending on deck played
      def PlayGames(self, deck_array: tuple, number_of_games: int, debug = False):
            print(f"Using {deck_array}\t Playing for {number_of_games} games.")
            deck_constructed = []
            hand_dict = {card: 0 for card in self.cards}
            for i, amount in enumerate(deck_array):
                  deck_constructed += [self.cards[i]]*amount
            game_output = []
            for j in tqdm(range(number_of_games)):
                  result = self.run_game(deck_constructed[:], hand_dict, 
                                         j%2, self.cache, debug)
                  game_output.append(result)
                  for card in hand_dict:
                       hand_dict[card] = 0
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
            for i, amount in enumerate(deck):
                  card = self.cards[i]
                  if amount < 0:
                        return False
                  if amount < card.min:
                        return False
                  if amount > card.max:
                        return False
                  cardsInDeck += amount
            if cardsInDeck != self.maxDeckSize:
                  return False
            return True
      

