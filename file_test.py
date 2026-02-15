"""
Debug file for testing individual modules
"""
from Tests.template import game

default_deck = game.CreateInitialDeck()
game.RunGames(default_deck, 100000)