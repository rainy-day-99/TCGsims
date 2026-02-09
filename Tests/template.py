import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Default variable
NORMAL = VanguardCard("Normal Unit", 2)

card_types = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA]

def run_game(main_deck: dict[VanguardCard, int], goingSecond: bool, cache = {}, debug = False):
    # Mulligan step
    hand: dict[VanguardCard, int] = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 3
    opponents_grade = 1 if goingSecond else 0
    damage_taken = 0
    for turn in range(1, last_turn + 1):        
        # Start of turn
        hand, main_deck = draw(hand, main_deck)

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck = draw(hand, main_deck)
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck = draw(hand, main_deck)

        # Main phase

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck, _ = draw(hand, main_deck, add=True)

        # Opponent's turn
        opponents_grade += 1
        for _ in range(random.choice([1, 2])):
            if damage_taken == 5:
                break
            hand, main_deck, damage = draw(hand, main_deck, add=False)
            if damage == OVER:
                break
            damage_taken += 1

    return (goingSecond, vanguard_grade)

def _mulligan(hand: dict[VanguardCard, int], deck: dict[VanguardCard, int]):
    _handsize = 5
    mulligan_range = random.sample(
        list(deck.keys()), 
        counts=list(deck.values()),
        k = _handsize*2)
    premulligan = mulligan_range[:5]
    postmulligan = mulligan_range[5:]
    _keep_one = [SENTINEL, PERSONA]
    card: VanguardCard
    for card in premulligan:
        if card.isTrigger:
            continue
        if card in _keep_one and hand[card] > 0:
            continue
        premulligan.remove(card)
        hand[card] += 1

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1
    for card in hand:
        deck[card] -= hand[card]
    return hand, deck

def value(data: np.array):
    grades = data[:, 1]
    return grades

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, value)