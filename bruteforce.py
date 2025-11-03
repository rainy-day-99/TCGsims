from gametools import Decklist, GameEnvironment

import itertools


def broad_search(env: GameEnvironment, num_sims: int = 500000):
    priorBestDeck = env.CreateInitialDeck()
    neighborhood = _expand(priorBestDeck, env)
    for deck in neighborhood:
        env.RunGames(deck, num_sims)
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


