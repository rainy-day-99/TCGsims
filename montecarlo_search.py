from scipy.stats import ttest_ind, norm
from vanguard.Veissrugr.lunarites import veissrugr as game
from gametools import Decklist
import itertools
import numpy as np
from time import time
from math import trunc

previousBestDeck = Decklist(game.cards, game.maxDeckSize)
testResults = {previousBestDeck: game.PlayGames(previousBestDeck, 2000)}

alpha = 0.05
minNumberOfSims = 2000

# For a binomial distribution, margin_of_error = 0.05%
margin_of_error = np.amax(testResults[previousBestDeck])/2000
z = norm.interval(1-alpha)[1]
maxNumberOfSims = round((z*np.std(testResults[previousBestDeck])/margin_of_error)**2)
print(f"Testing until {maxNumberOfSims} simulations.")
simIncrement = 1000

stillSearching = True
search_start = time()
while stillSearching:
    neighborhood = []
    newDecksMade = 0 
    test_duration = len(testResults[previousBestDeck])

    if test_duration < maxNumberOfSims:
        print("Creating cross neighborhood...")
        # Cross neighborhood of best deck. Swap every card for another card to generate neighborhood
        for add, drop in itertools.product(game.cards, repeat = 2):
            nearby_deck = previousBestDeck.clone()
            nearby_deck.recipe[add] += 1
            nearby_deck.recipe[drop] -= 1
            if not nearby_deck.isValid:
                continue
            if nearby_deck not in testResults:
                testResults[nearby_deck] = np.array([])
                newDecksMade += 1
            if nearby_deck not in neighborhood:
                neighborhood.append(nearby_deck)
    else:
        print("Creating star neighborhood...")
        # Star neighborhood of best deck. Every card can increase or decrease by one
        for alteration in itertools.combinations_with_replacement([-1,0,1], len(game.cards)):
            nearby_deck = previousBestDeck.clone()
            for increment, card in zip(alteration, game.cards):
                nearby_deck.recipe[card] += increment
            if not nearby_deck.isValid:
                continue
            if nearby_deck not in testResults:
                testResults[nearby_deck] = np.array([])
                newDecksMade += 1
            if nearby_deck not in neighborhood:
                neighborhood.append(nearby_deck)
                
    print(f" - Created {newDecksMade} decks this round. Testing...")
    decksTested = 0
    for deck in neighborhood:
        # Decks are tested proportionally to how much they have already been tested
        games_to_play = max(len(testResults[deck]), minNumberOfSims)

        if games_to_play >= maxNumberOfSims:
            continue
        if games_to_play*2 >= maxNumberOfSims:
            games_to_play = maxNumberOfSims - games_to_play
        if games_to_play == 0:
            continue
        if games_to_play > minNumberOfSims:
            compareMeans = ttest_ind(testResults[deck], testResults[previousBestDeck], equal_var=False)
            if compareMeans.pvalue < alpha: 
                continue

        decksTested += 1
        testResults[deck] = np.append(testResults[deck], game.PlayGames(deck, games_to_play))
        print(f"Result: {game.Score(testResults[deck]):.4f}")

    bestDeckInNeighborhood = max(neighborhood, key = lambda deck: game.Score(testResults[deck]))
    if decksTested > 0: 
        bestString = ', best deck changed'
        if bestDeckInNeighborhood == previousBestDeck:
            bestString = ''
        print("-----------------------------------------------")
        print(f" - {decksTested}/{len(neighborhood)} decks tested{bestString}")
        previousBestDeck = bestDeckInNeighborhood    
        print(f" - Best arrangement: {previousBestDeck}")        
        print(f" - Score: {game.Score(testResults[previousBestDeck]):.4f}\t- Mean: {np.mean(testResults[previousBestDeck]):4f}")

        minNumberOfSims += simIncrement
    else:
        stillSearching = False
    print("-----------------------------------------------")

print("Double-checking all decks played... ")
double_checking = True
while double_checking:
    decksTested = 0
    for deck in testResults:
        compareMeans = ttest_ind(testResults[deck], testResults[previousBestDeck], equal_var=False, alternative='less')
        if compareMeans.pvalue < alpha: 
            continue
        output = game.PlayGames(deck, minNumberOfSims)
        testResults[deck] = np.append(testResults[deck], output)
        minNumberOfSims += simIncrement
    if decksTested == 0:
        double_checking = False
    else:
        previousBestDeck = max(testResults.keys(), key = lambda x: game.Score(testResults[x]))

search_end = time()
duration = (search_end - search_start)/60
duration_minutes = trunc(duration)
duration_seconds = trunc((duration - duration_minutes) * 60)
second_timestamp = f"0{duration_seconds}" if duration_seconds < 10 else f"{duration_seconds}"
timestamp = f"{duration_minutes}:"+second_timestamp
print("Time to end:\t", timestamp)

import pandas as pd
pd.set_option("display.precision", 4)

variables = [card for card in game.cards if card.min != card.max]
d = {card.name: [] for card in variables}
d["Mean"] = []
d["Std. Dev."] = []
d["Score"] = []
d['n'] = []
table = pd.DataFrame(d)

counter = 0
for deck in testResults:
    sample = testResults[deck]
    mu = np.mean(sample)
    sigma = np.std(sample)
    score = game.Score(sample)
    table.loc[counter] = [deck.recipe[var] for var in variables] + [mu, sigma, score, len(sample)]
    counter += 1

for var in variables: 
    table[var.name] = pd.to_numeric(table[var.name], downcast='integer')
table['n'] = pd.to_numeric(table['n'], downcast='integer')
print(f"Total number of simulations run:\t{np.sum(table['n'])}")
print(table.sort_values('Score', ascending=False, ignore_index=True))

# 10046147