import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

# Default variable
NORMAL = VanguardCard("Normal Unit", 1)
FODDER = VanguardCard("Ride Fodder", 2, max = 12)
GANCELOT = VanguardCard("Gancelot", 2, min = 0, max = 0)

# Constants
TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)

card_types = [NORMAL, FODDER, GANCELOT, TRIGGER]

def run_game(cards: list[VanguardCard], 
             main_deck: list[int], 
             going_second: bool, 
             cache = {}, debug = False):

    # Mulligan step
    hand = [0 for card in cards]
    hand, main_deck = _mulligan(hand, cards, main_deck)
    
    vanguard_grade = 0
    last_turn = 4
    opponents_grade = 1 if going_second else 0
    damage_taken = 0
    utility = 0
    for turn in range(last_turn):        
        # Start of turn
        hand, main_deck, _ = draw(hand, cards, main_deck)
        main_deck[NORMAL.id] -= 1

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if hand[FODDER.id] > 0:
                hand[FODDER.id] -= 1
                utility += 1
            elif hand[GANCELOT.id] > 0:
                hand[GANCELOT.id] -= 1
                utility += 1
            elif hand[NORMAL.id] > 0:
                hand[NORMAL.id] -= 1
            else:
                hand[TRIGGER.id] -= 1
            if vanguard_grade == 1 and going_second:
                hand, main_deck, _ = draw(hand, cards, main_deck)

        # Main phase

        ## Exit before last drive checks
        if turn + 1 == last_turn:
            # hand, main_deck, _ = draw(hand, cards, main_deck)
            return(utility - hand[FODDER.id])

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck, _ = draw(hand, cards, main_deck)

        # Opponent's turn
        opponents_grade += 1
        for _ in range(random.choice([1, 2])):
            if damage_taken == 5:
                break
            hand, main_deck, _ = draw(hand, cards, main_deck, add=False)
            damage_taken += 1


def _mulligan(hand: list[int], cards: list[VanguardCard], deck: list[int]):
    _handsize = 5
    _mulligan_range = random.sample(
        population=cards, 
        counts=deck,
        k = _handsize * 2)
    for _ in range(_handsize):
        hand[_mulligan_range.pop().id] += 1
    _returned = hand[TRIGGER.id]
    hand[TRIGGER.id] = 0

    for _ in range(_returned):
        hand[_mulligan_range.pop().id] += 1
    for card in cards:
        deck[card.id] -= hand[card.id]
    return hand, deck

def difference(data: np.array):
    return data

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, difference)