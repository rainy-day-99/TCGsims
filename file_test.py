"""
Debug file for testing individual modules
"""
from Tests.discard import game

default_deck = game.CreateInitialDeck()
game.RunGames(default_deck, 10, True)

print(default_deck.results)
print("-"*100)
print(game.Score(default_deck))