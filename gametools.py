import numpy as np
from tqdm import tqdm
from functools import total_ordering

@total_ordering
class Card:
    cards_created = 0
    def __init__(self, name: str, min = 0, max = 99, *flag: str):
        self.name = name
        self.min = min
        self.max = max
      
        self.flag = flag

        self.id = Card.cards_created
        Card.cards_created += 1
    def __repr__(self):
        return self.name
    def __hash__(self):
        return self.id
    def __eq__(self, other):
          return self.id == other.id
    def __lt__(self, other):
          return (self.id < other.id)
                
    
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

class Decklist:
      def __init__(self, cards: list, deck_limit: int, initial_values: list = []):
            
            if initial_values: 
                  self.recipe: dict = {card: amount for card, amount in zip(cards, initial_values)}
            else:
                  layout = {card: card.min for card in cards}
                  deck_count = np.sum(list(layout.values()))
                  while deck_count < deck_limit:
                        for card in layout:
                              if layout[card] >= card.max:
                                    continue
                              if deck_count == deck_limit:
                                    break
                              layout[card] += 1
                              deck_count += 1
                  self.recipe: dict = layout
            self.max: int = deck_limit

            if type(cards[0]) == VanguardCard:
                 self.game = 'Vanguard'
            elif type(cards[0]) == MagicCard:
                 self.game = 'Magic'
            else:
                 self.game = 'n/a'
            self.last_error = ''

      def clone(self):
           cloned_deck = Decklist(list(self.recipe.keys()), self.max, list(self.recipe.values()))
           return cloned_deck

      def __hash__(self):
            return hash(tuple(sorted(self.recipe.items())))
      
      def __eq__(self, other):
            return (self.__hash__() == other.__hash__())
      
      def __repr__(self):
            return "Deck " + ".".join([f"{self.recipe[card]}" for card in self.recipe])
      
      @property
      def isValid(self):
            cardsInDeck = 0
            triggers = 0
            for card, amount in self.recipe.items():
                  if amount < 0:
                        self.last_error = f"{card} is below 0"
                        return False
                  if amount < card.min:
                        self.last_error = f"{card} is below minimum"
                        return False
                  if amount > card.max:
                        self.last_error = f"{card} is above maximum"
                        return False
                  cardsInDeck += amount
                  if self.game == 'Vanguard' and card.isTrigger:
                        triggers += amount
            if cardsInDeck != self.max:
                  self.last_error = f"Deck has {cardsInDeck} card, supposed to have {self.max}"
                  return False
            if self.game == 'Vanguard' and triggers != 16:
                 f"Deck has {triggers} triggers"
                 return False
            return True

class GameEnvironment:
      def __init__(self, cards: list, deck_size: int, run_game, interpret_results):
            
            self.cards = cards
            self.maxDeckSize = deck_size
            self.run_game = run_game
            self.interpret_results = interpret_results
                 
            # Optional for certain games
            self.cache = {}

      # Generic methods, since they will differ depending on deck played
      def PlayGames(self, deck: Decklist, number_of_games: int, debug = False):
            print(f"Playing {deck} for {number_of_games} games.")
            game_output = []
            for g in tqdm(range(number_of_games)):
                  result = self.run_game(deck.recipe.copy(), g%2, self.cache, debug)
                  game_output.append(result)
            if self.cache:
                  print(f"Cache size: {len(self.cache.keys())}")
            return np.array(game_output)
      
      def ReturnScore(self, results):
            return self.interpret_results(results) 
      

