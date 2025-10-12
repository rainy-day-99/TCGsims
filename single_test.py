from vanguard.base import template_sim as game

games_to_play = 1

default_deck = game.CreateInitialDeck()
debug_sim = (games_to_play == 1)

output = game.PlayGames(default_deck, games_to_play, debug_sim)
game.ReturnScore(output)