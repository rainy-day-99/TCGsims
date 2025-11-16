import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Default variable
NORMAL = VanguardCard("Normal Unit", 2)

card_types = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA]

def run_game(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    # Mulligan step
    hand = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 3
    opponents_grade = 1 if goingSecond else 0
    for turn in range(1, last_turn + 1):        
        # Start of turn
        hand, main_deck = _draw(hand, main_deck)

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck = _draw(hand, main_deck)
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck = _draw(hand, main_deck)

        # Main phase

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck = _draw(hand, main_deck)

        # Opponent's turn
        opponents_grade += 1
        hand, main_deck = _draw(hand, main_deck, False)

    return (goingSecond, vanguard_grade)

def _draw(hand: dict, deck: dict, add: bool = True):
    top_of_deck = random.choices(
        list(deck.keys()),   
        weights=list(deck.values()), k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
    if add:
        hand[draw] += 1
    return hand, deck

def _mulligan(hand: dict, deck: dict):
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