import scipy
from vanguard.test_veissrugr import veissrugr as game
import itertools
import numpy as np

from time import time
from math import trunc
previousBestDeck = game.CreateInitialDeck()


minNumberOfSims = 2000
maxNumberOfSims = 400000
simIncrement = 1000
alpha = 0.01
star_threshold = 0.75
testResults = {previousBestDeck: []}

bestDecksFound = 0
stillSearching = True
start = time()
while stillSearching:
    neighborhood = []
    print("Creating neighborhood...")
    newDecksMade = 0 
    test_duration = len(testResults[previousBestDeck])

    if test_duration < maxNumberOfSims * star_threshold:
        # If best deck is insufficiently tested, do a cross neighborhood 
        # This just swaps one card for another, and finds all possible combinations
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
    else:
        # If sufficiently tested, do a star neighborhood
        # All values for the decklist can be changed by 1 (assuming it's legal)
        adjustments = itertools.product((-1, 0, 1), repeat = len(previousBestDeck))
        for change in adjustments:
            newBase = []
            for i, card in enumerate(previousBestDeck):
                newBase.append(card + change[i])
            newDeck = tuple(newBase)
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
        gamesPlayed = len(testResults[deck])
        numSims = max(gamesPlayed, minNumberOfSims)
        if testResults[deck]:
            compareMeans = scipy.stats.ttest_ind(testResults[deck], testResults[previousBestDeck], equal_var=False)
            if compareMeans.pvalue < alpha and gamesPlayed > maxNumberOfSims / 4: 
                continue
        if numSims*2 >= maxNumberOfSims:
            numSims = maxNumberOfSims - gamesPlayed
        if numSims == 0:
            continue
        decksTested += 1
        testResults[deck] += game.PlayGames(deck, numSims)
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
        print(f" - Best score: {game.ReturnScore(testResults[previousBestDeck]):.4f}")
        print(f" - Best mean: {np.mean(testResults[previousBestDeck]):4f}")

        minNumberOfSims += simIncrement
    else:
        stillSearching = False
        bestDeck = bestDeckInNeighborhood
    print("-----------------------------------------------")

end = time()
duration = (end - start)/60
duration_minutes = trunc(duration)
duration_seconds = trunc((duration - duration_minutes) * 60)
second_timestamp = f"0{duration_seconds}" if duration_seconds < 10 else f"{duration_seconds}"
timestamp = f"{duration_minutes}:"+second_timestamp

print("Time to end:\t", timestamp)
neighborhood.sort(key = lambda deck: game.ReturnScore(testResults[deck]), reverse=True)
print("Top decks: ")
for selectedDeck in neighborhood:
    color = "\033[38;5;255m"
    if len(testResults[selectedDeck]) < maxNumberOfSims:
        continue
    if selectedDeck == bestDeck:
        color = "\033[38;5;220m"
    results = testResults[selectedDeck]
    print(f"{color}", [f"{game.cards[i]}: {count}" for i, count in enumerate(selectedDeck) if count != 0])
    print(f"{color} - Score: {game.ReturnScore(results):.4f},\t", f"n = {len(results)}\t")
    print(f"{color} - Mean: {np.mean(results):.4f}")
