from gametools import Card
import random

"""
    Generic methods used in several modules
"""

def draw(hand: list[int], deck: list[int], add: bool=True):
    if sum(deck) == 0:
        return hand, deck, None
    top_of_deck = random.choices(
        population=range(len(deck)),   
        weights=deck, 
        k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
    if add == True:
        hand[draw] += 1
    return hand, deck, draw

def debugprint(msg: str, debug_mode):
    if not debug_mode:
        return
    print(msg)