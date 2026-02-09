import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

defenders = 0
drawer = 0
NORMAL = VanguardCard("Normal Unit", 2, min = 27-drawer-defenders, max = 27-drawer-defenders)
CARD_DRAW = VanguardCard("Card Draw", 1, min = drawer, max = drawer)
DEFENDER = VanguardCard("Defender", 1, min = defenders, max = defenders)

# Default variable
TRIGGER = VanguardCard("Trigger", 0, trigger = True, min = 11, max = 12) # 4 heals, 7-8 crits
DRAW = VanguardCard("Draw", 0, trigger = True, min = 0, max = 4)
FRONT = VanguardCard("Front", 0, trigger = True, min = 0, max = 4)

card_types = [NORMAL, SENTINEL, PERSONA, 
              DEFENDER, CARD_DRAW,
              DRAW, FRONT, TRIGGER, OVER]

def run_game(main_deck: dict[VanguardCard, int], goingSecond: bool, cache = {}, debug = False):
    # Mulligan step
    hand: dict[VanguardCard, int] = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 5
    opponents_grade = 1 if goingSecond else 0
    over_checked = False
    for turn in range(1, last_turn + 1):        
        # Start of turn
        hand, main_deck, _ = draw(hand, main_deck)

        # Ride step
        if vanguard_grade < 3:
            for ride_cost in [PERSONA, NORMAL, CARD_DRAW, DRAW, TRIGGER, 
                              FRONT, DEFENDER, SENTINEL, OVER]:
                if hand[ride_cost] == 0:
                    continue
                elif ride_cost == PERSONA and hand[ride_cost] == 1:
                    continue
                hand[ride_cost] -= 1
                break 
            vanguard_grade += 1
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck, _ = draw(hand, main_deck)
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck, _ = draw(hand, main_deck)

        # Main phase
        while hand[CARD_DRAW] > 0:
            hand[CARD_DRAW] -= 1
            hand, main_deck, _ = draw(hand, main_deck)
        
        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        elif opponents_grade >= 3:
            drives = 3
        for _ in range(drives):
            hand, main_deck, drive_check = draw(hand, main_deck, add=True)
            if drive_check == OVER:
                hand[OVER] -= 1
                hand, main_deck, _ = draw(hand, main_deck)
            elif drive_check == DRAW:
                hand, main_deck, _ = draw(hand, main_deck)
        # Opponent's turn
        opponents_grade += 1
        hand, main_deck, damage_check = draw(hand, main_deck, add=False)
        if damage_check == OVER:
            hand, main_deck, _ = draw(hand, main_deck)
            over_checked = True
        elif damage_check == DRAW:
            hand, main_deck, _ = draw(hand, main_deck)

    # Based on first four turns of Hearluru aggro. Triggers are not assumed on either side
    # Five strongest attacks are taken, rest are guarded
    attacks = [35000, 25000, 25000, 25000, 15000, 15000, 15000, 15000, 5000]
    if over_checked:
        attack_to_skip = random.choice(attacks)
        attacks.remove(attack_to_skip)
    while hand[SENTINEL] > 0:
        hand[SENTINEL] -= 1
        for card in [PERSONA, NORMAL, CARD_DRAW, DEFENDER, DRAW, TRIGGER, FRONT, OVER]:
            if hand[card] == 0:
                continue
            hand[card] -= 1
            break
        attacks.pop(0)

    shield_value = 0
    shield_value += hand[NORMAL] * 5000
    shield_value += hand[CARD_DRAW] * 5000
    shield_value += hand[DEFENDER] * 10000
    shield_value += hand[TRIGGER] * 15000
    shield_value += hand[DRAW] * 10000
    shield_value += hand[FRONT] * 20000
    shield_value += hand[OVER] * 50000
    return(shield_value, sum(attacks))

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

def lived(data: np.array):
    total_shield = data[:, 0]
    total_attacks = data[:, 1]
    shield_diff = total_shield - total_attacks
    return np.where(shield_diff > 0, 1, 0)

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, lived)