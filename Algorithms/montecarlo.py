from gametools import Decklist, GameEnvironment
from os import get_terminal_size

from scipy.stats import ttest_ind
import itertools
import numpy as np
import emoji

def local_search(env: GameEnvironment, max_sims: int = 500000):
    priorBestDeck = env.CreateInitialDeck()
    all_decks = {priorBestDeck.key: priorBestDeck}

    min_sims = 1000
    if min_sims > max_sims:
        max_sims = 50000
    sim_increment = 1000

    decks_tested = 2
    while decks_tested > 1:
        print("".center(get_terminal_size()[0], '#'))

        neighborhood, all_decks, new_decks = _create_neighborhood(
            all_decks, priorBestDeck, env)
        
        print(f"Added {new_decks} new decks to the pool. Testing...\n")
        bestDeck, all_decks, decks_tested = _test_pool(
            neighborhood, all_decks, priorBestDeck, env, min_sims, max_sims)
        if bestDeck == priorBestDeck and decks_tested == 1:
            decks_tested = 0
        if env.Score(bestDeck, statistic='mean') > env.Score(priorBestDeck, statistic='mean'):
            priorBestDeck = bestDeck
        score = np.around(env.Score(priorBestDeck, statistic='mean'), 4)
        mu = np.around(np.mean(priorBestDeck.results, axis = 0), 4)
        print(f"\n - Best arrangement: {priorBestDeck}")
        print(f" - Score: {score:.4f}\t- Mean: {mu}")

        min_sims += sim_increment
    return all_decks


def _create_neighborhood(decks: dict, center: Decklist, env: GameEnvironment):
    keys = []
    decks_added = 0 
    for add, drop in itertools.product(env.variables, repeat = 2):
        nearby_deck = center.clone()
        nearby_deck.recipe[add] = min(add.max, nearby_deck.recipe[add] + 1)
        nearby_deck.recipe[drop] = max(drop.min, nearby_deck.recipe[drop] - 1)
        if not nearby_deck.legal:
            continue
        new_key = nearby_deck.key
        if new_key not in decks:
            decks_added += 1
            decks[new_key] = nearby_deck
        if new_key not in keys:
            keys.append(new_key)
    return(keys, decks, decks_added)

def _test_pool(keys: list, decks: dict, bestDeck: Decklist,
                env: GameEnvironment,
                minimum: int, maximum: int):
    alpha = 0.01
    localBestScore = 0
    localBestDeck = bestDeck
    test_count = 0
    for key in keys:
        deck: Decklist = decks[key]
        games_to_play = minimum
        if (games_to_play + deck.games_played) >= maximum:
            games_to_play = max(maximum - deck.games_played, 0)
        if games_to_play == 0:
            msg = emoji.emojize(f":stop_sign: {deck} has reached simulation limit")
            print(msg)
            continue
        if deck.games_played > 0:
            compareMeans = ttest_ind(env.Score(deck), 
                                     env.Score(decks[bestDeck.key]), 
                                     equal_var=False)
            if compareMeans.pvalue < alpha: 
                msg = emoji.emojize(f":fast-forward_button: {deck} skipped for time")
                print(msg)
                continue
        
        test_count += 1
        env.RunGames(deck, games_to_play)
        score = env.Score(deck, statistic = 'mean')
        if score > localBestScore:
            localBestScore = score
            localBestDeck = deck

    return localBestDeck, decks, test_count
    
# Unit test for montecarlo_search
if __name__ == "__main__":
    from Premium.gradelock import game
    testDeck = game.CreateInitialDeck()
    test_pool = dict()

    passed = emoji.emojize(":check_mark_button:")
    failed = emoji.emojize(":cross_mark:")

    neighbors_1, pool, decks_made_1 = _create_neighborhood(
        test_pool, testDeck, game)
    result = failed if (len(neighbors_1) == 0 or decks_made_1 != len(pool.keys())) else passed
    print(result, f"{decks_made_1} keys generated from _create_neighborhood ")

    neighbors_2, pool, decks_made_2 = _create_neighborhood(
        pool, testDeck, game)
    result = failed if decks_made_2 > 0 else passed 
    print(result, f"{decks_made_2} new decks created with same center")

    test_count = 1000
    bestInPool, pool, test_count = _test_pool(neighbors_2, pool, testDeck, game, test_count, 2000)
    decks_untested = 0
    results_empty = 0
    deck: Decklist
    result1 = passed
    result2 = passed
    for key in neighbors_2:
        deck = pool[key]
        if deck.games_played != test_count:
            decks_untested += 1
            result1 = failed
        if deck.results.size == 0:
            results_empty += 1
            result2 = failed
    print(result1, f"{decks_untested} decks with unnatural sim count")
    print(result2, f"{results_empty} decks with empty results array")

