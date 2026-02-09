"""
Debug file for testing individual modules
"""
from Vyrgilla.advanced import game

default_deck = game.CreateInitialDeck()
game.RunGames(default_deck, 10)

print(default_deck.results)
print(game.Score(default_deck))
print(game.Score(default_deck, statistic="mean"))