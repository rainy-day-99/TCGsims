import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

# Default variable
NORMAL = VanguardCard("Normal Unit", 1)
FODDER = VanguardCard("Ride Fodder", 2, max = 12)

# Constants
TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)

card_types = [NORMAL, FODDER, TRIGGER]

def run_game(cards: list[VanguardCard], 
             main_deck: list[int], 
             going_second: bool, 
             cache = {}, debug = False):

    # Mulligan step
    hand = [0 for _ in main_deck]
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 4
    opponents_grade = 1 if going_second else 0
    damage_taken = 0
    utility = 0
    for turn in range(last_turn):        
        # Start of turn
        hand, main_deck, _ = draw(hand, main_deck)

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if hand[FODDER.id] > 0:
                hand[FODDER.id] -= 1
                utility += 1
            elif hand[NORMAL.id] > 0:
                hand[NORMAL.id] -= 1
            else:
                hand[TRIGGER.id] -= 1
            if vanguard_grade == 1 and going_second:
                hand, main_deck, _ = draw(hand, main_deck)

        # Main phase

        ## Exit before last drive checks
        if turn + 1 == last_turn:
            # hand, main_deck, _ = draw(hand, main_deck)
            return(utility - hand[FODDER.id])

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck, _ = draw(hand, main_deck)

        # Opponent's turn
        opponents_grade += 1
        for _ in range(random.choice([1, 2])):
            if damage_taken == 5:
                break
            hand, main_deck, _ = draw(hand, main_deck, add=False)
            damage_taken += 1


def _mulligan(hand: list[int], deck: list[int]):
    _handsize = 5
    _indices = range(len(deck))
    _mulligan_range = random.sample(
        population=_indices, 
        counts=deck,
        k = _handsize * 2)
    for _ in range(_handsize):
        hand[_mulligan_range.pop()] += 1
    _returned = hand[TRIGGER.id]
    hand[TRIGGER.id] = 0

    for _ in range(_returned):
        hand[_mulligan_range.pop()] += 1
    for i in _indices:
        deck[i] -= hand[i]
    return hand, deck

def difference(data: np.array):
    return data

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, difference)