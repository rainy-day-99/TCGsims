import random as random
import numpy as np
from gametools import GameEnvironment, MagicCard

ONE = MagicCard('1-drop', 1, max = 30)
TWO = MagicCard('2-drop', 2, max = 30)
THREE = MagicCard('3-drop', 3, max = 30)
FOUR = MagicCard('4-drop', 4, max = 30)
FIVE = MagicCard('5-drop', 5, max = 30)
SIX = MagicCard('6-drop', 6, max = 30)

LAND = MagicCard('Land', 0, min = 30, max = 45)
SOL_RING = MagicCard('Sol Ring', 1, min = 1, max = 1)

card_types = [ONE, TWO, THREE, FOUR, FIVE, SIX, LAND, SOL_RING]

def run_game(library: dict, goingSecond: bool, cache = {}, debug = False):
    # Mulligan step
    for to_bottom in [0, 0, 1, 2, 3]:
        hand = {card: 0 for card in library}
        bottom_deck = []
        mulligan_range = random.sample(
            list(library.keys()), 
            counts=list(library.values()),
            k = 7)
        for card in mulligan_range:
            hand[card] += 1
        while len(bottom_deck) < to_bottom:
            if hand[LAND] > 3:
                hand[LAND] -= 1
                bottom_deck.append(LAND)
                continue
            for spell in [SIX, FIVE, FOUR, THREE, TWO, ONE]:
                if hand[spell] == 0:
                    continue
                hand[spell] -= 1
                bottom_deck.append(spell)
                break
        if to_bottom == 3:
            break
        upper_limit = 5 if to_bottom == 0 else 4
        if hand[LAND] + hand[SOL_RING] < 3:
            continue
        if hand[LAND] + hand[SOL_RING] > upper_limit:
            continue
    for card in hand:
        library[card] -= hand[card]

    # Including commander
    hand[THREE] += 1 

    field_mv = 0
    turn_mv = []
    mana_sources = 0
    last_turn = 7
    for turn in range(1, last_turn + 1):        
        # Start of turn
        hand, library = _draw(hand, library)

        # PLay a land if possible
        if hand[LAND] > 0:
            hand[LAND] -= 1
            mana_sources += 1

        # Greedy strategy: play highest cost possible
        mana_to_spend = mana_sources
        while mana_to_spend > 0:
            if hand[SOL_RING] > 0:
                hand[SOL_RING] -= 1
                mana_sources += 2
                mana_to_spend -= 1
                if mana_to_spend == 0:
                    break
                else:
                    mana_to_spend += 2
            casted_spell = False
            for spell in [SIX, FIVE, FOUR, THREE, TWO, ONE]:
                if hand[spell] == 0:
                    continue
                if spell.mv > mana_to_spend:
                    continue
                hand[spell] -= 1
                mana_to_spend -= spell.mv
                field_mv += spell.mv
                casted_spell = True
                break
            if not casted_spell:
                mana_to_spend = 0
            
        # Add field's mana value to cumulative total
        turn_mv.append(field_mv)

    return turn_mv

def _draw(hand: dict, deck: dict, add: bool = True):
    top_of_deck = random.choices(
        list(deck.keys()),   
        weights=list(deck.values()), k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
    if add:
        hand[draw] += 1
    return hand, deck

def value(data: np.array):
    cumulative_mv = np.sum(data, 1)
    return cumulative_mv

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 99, run_game, value)