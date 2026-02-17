import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

# Default variable
NORMAL = VanguardCard("Normal Unit", 1)
TARGET = VanguardCard("Target", 2, min = 0, max = 8)

# Constants
TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 0, max = 0)
PERSONA = VanguardCard("Persona Ride", 3, min = 0, max = 0)


card_types = [NORMAL, TARGET, TRIGGER, OVER, SENTINEL, PERSONA]

def run_game(cards: list[VanguardCard], 
             main_deck: list[int], 
             going_second: bool, 
             cache = {}, debug = False):
    # Mulligan step
    hand = [0 for card in cards]
    hand, main_deck = _mulligan(hand, cards, main_deck)
    
    vanguard_grade = 0
    last_turn = 0
    opponents_grade = 1 if going_second else 0
    damage_taken = 0
    for _ in range(last_turn):        
        # Start of turn
        hand, main_deck, _ = draw(hand, cards, main_deck)

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if vanguard_grade == 1 and going_second:
                hand, main_deck, _ = draw(hand, cards, main_deck)
        elif hand[PERSONA.id] > 0:
            hand[PERSONA.id] -= 1
            hand, main_deck, _ = draw(hand, cards, main_deck)

        # Main phase

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
            hand, main_deck, damage = draw(hand, cards, main_deck, add=False)
            if damage == OVER:
                hand, main_deck, _ = draw(hand, cards, main_deck)
                break
            damage_taken += 1

    frequency = [0 for i in range(8 + 1)]
    frequency[hand[TARGET.id]] = 1
    return tuple([going_second] + frequency)

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

def value(data: np.array):
    hits = data[:, 2]
    return hits

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, value)