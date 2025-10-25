from vanguard.Lianorn.rosarium import lianorn as game
from gametools import Decklist
from itertools import product

import pandas as pd
import numpy as np 


deck: Decklist
seed_deck = Decklist(game.cards, game.maxDeckSize)
valid_decks = [seed_deck]
while True:
    neighborhood = []
    for deck in valid_decks:
        for add, drop in product(game.cards, repeat = 2):
            if add == drop:
                continue
            new_deck = deck.clone()
            new_deck.recipe[add] += 1
            new_deck.recipe[drop] -= 1
            if not new_deck.isValid:
                continue
            if new_deck in neighborhood:
                continue
            if new_deck in valid_decks:
                continue
            neighborhood.append(new_deck)
    if neighborhood:
        valid_decks += neighborhood
    else:
        break

variables = [card for card in game.cards if card.min != card.max]
print("Variables considered: ", variables)
print(f"Testing {len(valid_decks)} decks total")
n = 500000
print(f"Running n = {n} simulations per deck...\n")

d = {card.name: [] for card in variables}
d["Mean"] = []
d["Standard Deviation"] = []
d["Score"] = []
table = pd.DataFrame(d)

for i, deck in enumerate(valid_decks):
    results = game.PlayGames(deck, n)
    mu = np.mean(results)
    sigma = np.std(results)
    score = game.ReturnScore(results)
    table.loc[i] = [int(deck.recipe[var]) for var in variables] + [mu, sigma, score]

pd.set_option("display.precision", 4)
for var in variables:
    table[var.name] = pd.to_numeric(table[var.name], downcast='integer')
print("\n")
print(table.sort_values("Score", ascending = False))