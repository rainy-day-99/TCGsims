from gametools import Decklist, GameEnvironment
from scipy.stats import ttest_ind
import itertools


def broad_search(env: GameEnvironment, max_sims: int = 500000):
    priorBestDeck = env.CreateInitialDeck()
    neighborhood = _expand(priorBestDeck, env)
    searching = True
    while searching:
        neighborhood, searching = _iterate_through_neighborhood(neighborhood, env, max_sims)
    all_decks = dict()
    for deck in neighborhood:
        all_decks[deck.key] = deck
    return all_decks


def _expand(center: Decklist, env: GameEnvironment):
    decks = [center]
    decks_added = 1
    while decks_added > 0:
        decks_added = 0
        new_decks = []
        for deck in decks:
            for add, drop in itertools.product(env.variables, repeat = 2):
                nearby_deck = deck.clone()
                nearby_deck.recipe[add] = min(add.max, nearby_deck.recipe[add] + 1)
                nearby_deck.recipe[drop] = max(drop.min, nearby_deck.recipe[drop] - 1)
                if not nearby_deck.legal:
                    continue
                if nearby_deck in new_decks:
                    continue
                if nearby_deck not in decks:
                    decks_added += 1
                    new_decks.append(nearby_deck)
        decks += new_decks
    return(decks)

def _iterate_through_neighborhood(decks: dict, env: GameEnvironment, maximum: int):
    try:
        decks.sort(key = lambda deck: env.Score(deck, statistic="mean"), reverse = True)
    except:
        pass
    best_deck = decks[0]
    minimum = 10000
    alpha = 0.01
    deck: Decklist
    decks_tested = 0
    for deck in decks:
        num_sims = max(minimum, deck.games_played)
        if deck.games_played + num_sims > maximum:
            num_sims = maximum - deck.games_played
        if deck.games_played > 0:
            compare_scores = ttest_ind(env.Score(deck), env.Score(best_deck))
            if compare_scores.pvalue < alpha:
                continue
        env.RunGames(deck, num_sims)
        decks_tested += 1
    if decks_tested > 2:
        return decks, True
    return decks, False

