from functools import total_ordering
import numpy as np
import emoji
"""
      Contains three classes:
      - Card: a generic object for holding card info 
      - Decklist: holds a dictionary with Card objects as keys, and values are card amounts
      - GameEnvironment: manager for running simulations. 
"""

@total_ordering
class Card:
    cards_created = 0
    def __init__(self, name: str, min = 0, max = 99, *flag: str):
        self.name = name
        self.min = min
        self.max = max
      
        self.flag = flag

        self.priority = Card.cards_created
        Card.cards_created += 1
    def __repr__(self):
        return self.name
    def __hash__(self):
        return self.priority
    def __eq__(self, other):
          return self.priority == other.priority
    def __lt__(self, other):
          return (self.priority < other.priority)
    
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

"""
    Decklist class for holding a particular deck dictionary

    Object is meant to be cloned and modified, and holds method
    for determining if it's a valid deck
"""
class Decklist:
      def __init__(self, 
                   cards: list, deck_limit: int, 
                   initial_values: list = []):
            
            if initial_values: 
                  self.recipe: dict = {card: amount for card, amount in zip(cards, initial_values)}
            else:
                  layout = {card: card.min for card in cards}
                  deck_count = sum(list(layout.values()))
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

            self.results: np.array = np.array([])
            self.games_played: int = 0

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

      @property
      def key(self):
            k = tuple(self.recipe[card] for card in self.recipe if card.min != card.max)
            return tuple(k)
      
      def __eq__(self, other):
            return (self.recipe == other.recipe)
      
      def __repr__(self):
            return "Deck " + ".".join([f"{self.recipe[card]}" for card in self.recipe])
      
      @property
      def legal(self):
            cardsInDeck = 0
            triggers = 0
            for card, amount in self.recipe.items():
                  if amount < 0:
                        self.last_error = f"{card} is below 0!"
                        return False
                  if amount < card.min:
                        self.last_error = f"{card} is below minimum!"
                        return False
                  if amount > card.max:
                        self.last_error = f"{card} is above maximum!"
                        return False
                  cardsInDeck += amount
                  if self.game == 'Vanguard' and card.isTrigger:
                        triggers += amount
            if cardsInDeck != self.max:
                  self.last_error = f"Deck has {cardsInDeck} card, supposed to have {self.max}!"
                  return False
            if self.game == 'Vanguard' and triggers != 16:
                 self.last_error = f"Deck has {triggers} triggers!"
                 return False
            return True

"""
      This is the container for all relevant information in a given module.
      - cards: the card variables for decklist assembly
      - deck_size: the total number of cards in the deck recipe
      - run_game: function that runs one simulation with a decklist
      - interpret_results: translates simulation output into relevant data for analysis
"""
class GameEnvironment:
      def __init__(self, 
                   cards: list, deck_size: int, 
                   run_game, interpret_results):
            
            self.cards = cards
            self.deck_size = deck_size

            self.run_game = run_game
            self.interpret_results = interpret_results
                 
            self.variables = [card for card in cards if card.min != card.max]
            
            # Optional for certain games
            self.cache = {}

      # Generic methods, since they will differ depending on deck played
      def RunGames(self, deck: Decklist, number_of_games: int, debug = False):
            game_output = []
            done = emoji.emojize(":green_circle:")
            playing = emoji.emojize(":hollow_red_circle:")

            for g in range(number_of_games):
                  print(f"\r{playing} Played {g}/{number_of_games} games with {deck}", end = "", flush=True)
                  result = self.run_game(deck.recipe.copy(), g%2, self.cache, debug)
                  game_output.append(result)
            if self.cache:
                  print(f"Cache size: {len(self.cache.keys())}")
            print(f"\r{done} Played {number_of_games}/{number_of_games} games with {deck}", end = "\n", flush=True)
            
            if deck.results.size == 0:
                  deck.results = np.array(game_output)
            else:
                  deck.results = np.concatenate((deck.results, np.array(game_output)))
            deck.games_played += number_of_games
      
      def Score(self, deck: Decklist, statistic: str = ''):
            """
                  Changes N-dimensional array into a 1-D array for analysis
            """
            scored_results = self.interpret_results(deck.results)
            if scored_results.shape != (deck.games_played,):
                  msg_error = f"{self.interpret_results.__name__} yields a {scored_results.shape}-shaped array"
                  raise Exception(msg_error)
            if statistic == 'mean':
                  return np.mean(scored_results)
            if statistic == 'std':
                  return np.mean(scored_results)
            return scored_results
      
      def CreateInitialDeck(self):
            deck = Decklist(self.cards, self.deck_size)
            if not deck.legal:
                  raise Exception(deck.last_error)
            return(deck)