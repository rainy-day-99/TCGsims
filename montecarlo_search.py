from scipy.stats import ttest_ind
from vanguard.gradelock import test as game
import itertools
import numpy as np
from time import time
from math import trunc

previousBestDeck = game.CreateInitialDeck()

minNumberOfSims = 2000
maxNumberOfSims = 400000
simIncrement = 1000
alpha = 0.01
testResults = {previousBestDeck: []}

bestDecksFound = 0
stillSearching = True
search_start = time()
while stillSearching:
    neighborhood = []
    print("Creating neighborhood...")
    newDecksMade = 0 
    test_duration = len(testResults[previousBestDeck])

    # Cross neighborhood of best deck. Swap every card for another card to generate neighborhood
    for add, drop in itertools.product(range(len(game.cards)), repeat = 2):
        newAmounts = [i for i in previousBestDeck]
        newAmounts[add] += 1
        newAmounts[drop] -= 1
        newDeck = tuple(newAmounts)
        if not game.CheckIfValid(newDeck):
            continue
        if newDeck not in testResults:
            testResults[newDeck] = []
            newDecksMade += 1
        if newDeck not in neighborhood:
            neighborhood.append(newDeck)
                
    print(f" - Created {newDecksMade} decks this round. Testing...")
    decksTested = 0
    for deck in neighborhood:
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
        testResults[deck] += game.PlayGames(deck, games_to_play)
        print(f"Result: {game.ReturnScore(testResults[deck]):.4f}")

    bestDeckInNeighborhood = max(neighborhood, key = lambda deck: game.ReturnScore(testResults[deck]))
    if decksTested > 0: 
        bestString = ', best deck changed'
        if bestDeckInNeighborhood == previousBestDeck:
            bestString = ''
        print(f" - {decksTested}/{len(neighborhood)} decks tested{bestString}")
        previousBestDeck = bestDeckInNeighborhood    
        variables = [f"{game.cards[i]}: {count}" for i, count in enumerate(previousBestDeck) if count != 0]
        print(f" - Best arrangement: {variables}")        
        print(f" - Score: {game.ReturnScore(testResults[previousBestDeck]):.4f}")
        print(f" - Mean: {np.mean(testResults[previousBestDeck]):4f}")

        minNumberOfSims += simIncrement
    else:
        stillSearching = False
        bestDeck = bestDeckInNeighborhood
    print("-----------------------------------------------")

search_end = time()
duration = (search_end - search_start)/60
duration_minutes = trunc(duration)
duration_seconds = trunc((duration - duration_minutes) * 60)
second_timestamp = f"0{duration_seconds}" if duration_seconds < 10 else f"{duration_seconds}"
timestamp = f"{duration_minutes}:"+second_timestamp
print("Time to end:\t", timestamp)

neighborhood.sort(key = lambda deck: game.ReturnScore(testResults[deck]), reverse=True)
best_decks = neighborhood[:5]
print("Top five decks: ")
for selectedDeck in reversed(best_decks):
    color = "\033[38;5;255m"
    if selectedDeck == bestDeck:
        color = "\033[38;5;220m"
    results = testResults[selectedDeck]
    print(f"{color}", [f"{game.cards[i]}: {count}" for i, count in enumerate(selectedDeck) if count != 0])
    print(f"{color} - Score: {game.ReturnScore(results):.4f},\t", f"n = {len(results)}\t")
    print(f"{color} - Mean: {np.mean(results):.4f}")
