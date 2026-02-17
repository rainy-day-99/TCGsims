from functools import total_ordering
import numpy as np
from scipy.stats import mode
import emoji
"""
      Contains three classes:
      - Card: a generic object for holding card info 
      - Decklist: holds a dictionary with Card objects as keys, and values are card amounts
      - GameEnvironment: manager for running simulations. 
"""

class Card:
    cards_created = 0
    def __init__(self, name: str, min = 0, max = 99, *flag: str):
        self.id = Card.cards_created
        Card.cards_created += 1

        self.name = name
        self.min = min
        self.max = max
      
        self.flag = flag

    def __repr__(self):
        return self.name
    def __hash__(self):
        return self.id
    def __eq__(self, other):
        if other == None:
            return False
        return self.id == other.id
    def __int__(self):
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

"""
    Decklist class for holding a particular deck dictionary

    Object is meant to be cloned and modified, and holds method
    for determining if it's a valid deck
"""
class Decklist:
    def __init__(self, 
        cards: list[Card], deck_limit: int, 
        initial_values: list[int] = []):

        self.cards = cards
        self.cards.sort(key = lambda card: card.id)
        if initial_values: 
            self.recipe: list[int] = [amount for amount in initial_values]
        else:
            layout = [card.min for card in cards]
            deck_count = sum(layout)
            while deck_count < deck_limit:
                for card in cards:
                    if layout[card.id] == card.max:
                        continue
                    if deck_count == deck_limit:
                        break
                    layout[card.id] += 1
                    deck_count += 1
            self.recipe: list[int] = layout
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
        cloned_deck = Decklist(self.cards, self.max, self.recipe)
        return cloned_deck

    @property
    def key(self):
        k = tuple(self.recipe)
        return tuple(k)
    
    def __eq__(self, other):
        return (self.key == other.key)
    
    def __repr__(self):
        return f"Deck {self.recipe}"
    
    @property
    def legal(self):
        cardsInDeck = 0
        triggers = 0
        for card, amount in zip(self.cards, self.recipe):
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
        cards: list[Card], deck_size: int, 
        sim_function, interpret_results):
        
        self.cards = cards
        self.deck_size = deck_size

        self.run_game = sim_function
        self.interpret_results = interpret_results
                
        self.variables = [card for card in cards if card.min != card.max]
        
        # Optional for certain games
        self.cache = {}

    # Generic methods, since they will differ depending on deck played
    def RunGames(self, deck: Decklist, number_of_games: int, debug = False):
        done = emoji.emojize(":green_circle:")
        playing = emoji.emojize(":hollow_red_circle:")
        stopped = emoji.emojize(":stop_sign:")
        if number_of_games == 0:
            print(f"{stopped} Played no games with {deck}")
            return
        game_output = []

        for g in range(number_of_games):
            print(f"{playing} Played {g}/{number_of_games} games with {deck}", end = "\r", flush=True)
            result = self.run_game(deck.cards, deck.recipe.copy(), g%2, self.cache, debug)
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
            "mean": returns the average of the results
        """
        scored_results = self.interpret_results(deck.results)
        if scored_results.shape != (deck.games_played,):
            msg_error = f"{self.interpret_results.__name__} yields a {scored_results.shape}-shaped array"
            raise Exception(msg_error)
        if statistic == 'mean':
            return np.mean(scored_results)
        if statistic == 'std':
            return np.mean(scored_results)
        if statistic == 'mode':
            return mode(scored_results, axis=None)[0]
        return scored_results
    
    def CreateInitialDeck(self):
        deck = Decklist(self.cards, self.deck_size)
        if not deck.legal:
            raise Exception(deck.last_error)
        return(deck)