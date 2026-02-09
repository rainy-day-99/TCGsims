import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
# Default variable
NORMAL = VanguardCard("Normal Unit", 2)
TARGET = VanguardCard("Target Unit", 1, min = 1, max = 5)

card_types = [NORMAL, TRIGGER, TARGET]

def run_game(main_deck: dict[VanguardCard, int], goingSecond: bool, cache = {}, debug = False):
    card: VanguardCard
    deck = []
    for card in main_deck:
        deck += [card] * main_deck[card]
    random.shuffle(deck)
    hand = []
    for _ in range(5):
        hand.append(deck.pop(0))
    bottom_deck = []
    while TRIGGER in hand:
        hand.remove(TRIGGER)
        bottom_deck.append(TRIGGER)
    if TRIGGER in hand:
        print("AGH!")
    for card in bottom_deck:
        hand.append(deck.pop(0))
    for card in bottom_deck:
        deck.append(card)

    frequency = [0 for i in range(TARGET.max + 1)]
    frequency[hand.count(TARGET)] = 1
    return frequency

def atleast(data: np.array):
    return 1 - data[:, 0]

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, atleast)