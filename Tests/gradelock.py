import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw, debugprint

# Default variable
GRADE_1 = VanguardCard("Grade 1", 1, max = 16)
GRADE_2 = VanguardCard("Grade 2", 2, max = 16)
GRADE_3 = VanguardCard("Grade 3", 3, max = 16)

# Constants
STARTER = VanguardCard("V Starter", 0, min = 0, max = 0)
TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)

card_types = [GRADE_1, GRADE_2, GRADE_3, STARTER, TRIGGER, OVER]

def run_game(cards: list[VanguardCard], 
             main_deck: list[int], 
             going_second: bool, 
             cache = {}, debug = False):
    # Mulligan step
    hand = [0 for card in cards]
    hand, main_deck = _mulligan(hand, cards, main_deck)
    
    vanguard = STARTER
    opponents_grade = 1 if going_second else 0
    damage_taken = 0
    
    last_turn = 3
    for turn in range(last_turn):        
        # Start of turn
        hand, main_deck, _ = draw(hand, cards, main_deck)
        
        # Ride step
        ride_target = None
        for card in cards:
            if hand[card.id] == 0:
                continue
            elif card.grade != vanguard.grade + 1:
                continue
            ride_target = card
        if ride_target != None:
            hand[ride_target.id] -= 1
            vanguard = ride_target
            debugprint(f" - Rode {ride_target}", debug)

        # Main phase

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
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

    return (going_second, vanguard.grade)

def _mulligan(hand: list[int], cards: list[VanguardCard], deck: list[int]):
    _handsize = 5
    _mulligan_range = random.sample(
        population=cards, 
        counts=deck,
        k = _handsize * 2)
    for _ in range(_handsize):
        hand[_mulligan_range.pop().id] += 1

    _returned = hand[TRIGGER.id] + hand[OVER.id]
    hand[TRIGGER.id] = 0
    hand[OVER.id] = 0

    for unit in [GRADE_1, GRADE_2, GRADE_3]:
        if hand[unit.id] == 0:
            continue
        _returned += hand[unit.id] - 1
        hand[unit.id] = 1
    for _ in range(_returned):
        hand[_mulligan_range.pop().id] += 1
    for card in cards:
        deck[card.id] -= hand[card.id]

    return hand, deck

def value(data: np.array):
    grades = data[:, 1]
    return np.where(grades == 3, 1, 0)

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 49, run_game, value)