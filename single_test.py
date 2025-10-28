from vanguard.Veissrugr.lunarites import veissrugr as game
from gametools import Decklist
import numpy as np
import pandas as pd
import pprint as pp

games_to_play = 10000

default_deck = Decklist(game.cards, game.maxDeckSize)
debug_sim = (games_to_play == 1)

output = game.PlayGames(default_deck, games_to_play, debug_sim)
distribution = np.unique_counts(output)
d = {
    'Counts': distribution.counts,
    'Frequency': [c/games_to_play for c in distribution.counts]
}   

pp.pprint(default_deck.recipe)
print("-------------------------------------")
print(pd.DataFrame(d, index = distribution.values))
print(np.mean(output))