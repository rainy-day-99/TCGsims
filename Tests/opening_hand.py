import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
# Default variable
NORMAL = VanguardCard("Normal Unit", 2)
TARGET = VanguardCard("Target Unit", 1, min = 1, max = 4)

card_types = [NORMAL, TRIGGER, TARGET]

def run_game(main_deck: dict[VanguardCard, int], goingSecond: bool, cache = {}, debug = False):
    card: VanguardCard
    premulligan = random.sample(
        list(main_deck.keys()),
        counts=list(main_deck.values()),
        k=5)
    hand = {NORMAL: 0, TRIGGER: 0, TARGET: 0}
    for card in premulligan:
        main_deck[card] -= 1
        hand[card] += 1

    redraw = hand[TRIGGER]
    postmulligan = random.sample(
        list(main_deck.keys()),
        counts=list(main_deck.values()),
        k=redraw)
    hand[TRIGGER] = 0
    for card in postmulligan:
        hand[card] += 1
        main_deck[card] -= 1
    main_deck[TRIGGER] += redraw

    for turn in range(0):
        draw = random.choices(
            list(main_deck.keys()),
            weights=list(main_deck.values()),
            k=1)[0]
        main_deck[draw] -= 1
        hand[draw] += 1

    frequency = []
    for i in range(10):
        if i == hand[TARGET]:
            frequency.append(1)
        else:
            frequency.append(0)
    return frequency

def atleast(data: np.array):
    return data[:, 1] + data[:, 2]

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, atleast)