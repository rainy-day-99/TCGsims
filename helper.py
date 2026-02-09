from gametools import Card
import random

"""
    Generic methods used in several modules
"""

def draw(hand: dict[Card, int], deck: dict[Card, int], add: bool=True):
    deck_values = list(deck.values())
    if sum(deck_values) == 0:
        return hand, deck, None
    top_of_deck = random.choices(
        list(deck.keys()),   
        weights=deck_values, 
        k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
    if add == True:
        hand[draw] += 1
    return hand, deck, draw

def topX(hand: dict[Card, int], deck: dict[Card, int], 
         range: int, search_targets: list[Card], cards_to_add: int = 1):
    deck_values = list(deck.values())
    cards_in_deck = len(deck_values)
    if cards_in_deck == 0:
        return hand, deck, []
    search_space = random.sample(
        list(deck.keys()), 
        counts=list(deck.values()), 
        k=min(search_targets, cards_in_deck))
    targets_found = []
    for _ in range(cards_to_add):
        for target in search_targets:
            if target not in search_space:
                continue
            targets_found.append(target)
            break
    for card in targets_found:
        hand[card] += 1
        deck[card] -= 1
    return hand, deck, targets_found
