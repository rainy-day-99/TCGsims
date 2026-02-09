import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

TRIGGER = VanguardCard("Trigger", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Dragveda", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Vyrgilla cards
ALFKNIGHTS = VanguardCard("Alfknights", 3, min = 4, max = 4)

# Variables
NORMAL = VanguardCard("Normal", 2)
FANVARE = VanguardCard("Fanvare", 3, min = 2, max = 3)
ULTIMATE = VanguardCard("Ult Skill", 2, unit = False, min = 2, max = 3)

card_types = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA, 
              ALFKNIGHTS, FANVARE, ULTIMATE]

def run_game(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    goingSecond = False
    # Mulligan step
    hand = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 5
    opponents_grade = 1 if goingSecond else 0
    
    rewrites_per_turn = []
    fanvare_per_turn = []
    drop = {FANVARE: 0, ULTIMATE: 0}
    field = {FANVARE: 0, ULTIMATE: 0}
    soul = {FANVARE: 0, ALFKNIGHTS: 0}
    damage_taken = 0
    for turn in range(1, last_turn + 1):      
        # Start of turn
        hand, main_deck, _ = draw(hand, main_deck)
        rewrite = False

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck, _ = draw(hand, main_deck)
            if vanguard_grade == 3 and main_deck[NORMAL] > 0:
                main_deck[NORMAL] -= 1
                hand[NORMAL] += 1
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck, _ = draw(hand, main_deck)

        # Main phase
        ## Rewrite if the opponent's on grade 3
        if vanguard_grade >= 3 and opponents_grade >= 3 and hand[ALFKNIGHTS] > 0:
            hand[ALFKNIGHTS] -= 1
            soul[ALFKNIGHTS] += 1
            rewrite = True
            ### Search for Fanvare/Ultimate Skill if possible
            for target in [FANVARE, ULTIMATE]:
                if main_deck[target] > 0:
                    main_deck[target] -= 1
                    hand[target] += 1
                elif drop[target] > 0:
                    drop[target] -= 1
                    hand[target] += 1

        if opponents_grade >= 3 and hand[FANVARE] > 0 and hand[ULTIMATE] > 0:
            ## Call Fanvare, use soul-blast
            hand[FANVARE] -= 1
            field[FANVARE] += 1
            if soul[FANVARE] > 0:
                soul[FANVARE] -= 1
                drop[FANVARE] += 1
            ## Play Ultimate Skill for turn
            hand[ULTIMATE] -= 1
            field[ULTIMATE] += 1

        # Battle phase
        base_drives = 1 if vanguard_grade < 3 else 2
        drives = base_drives
        if rewrite:
            drives += 1
        if opponents_grade == 0:
            drives = 0
        while drives > 0:
            drives -= 1
            hand, main_deck, drive_check = draw(hand, main_deck, add=False)
            if drive_check == OVER:
                hand, main_deck, _ = draw(hand, main_deck)
                drives += base_drives
            else:
                hand[drive_check] += 1

        # End of turn
        if vanguard_grade >= 3:
            # Count rewriting Alfknights for turn 
            if rewrite:
                rewrites_per_turn.append(1)
            else:
                rewrites_per_turn.append(0)
            # Send Fanvare to soul to draw
            fanvare_draw = 0
            if field[ULTIMATE] > 0:
                field[ULTIMATE] -= 1
                drop[ULTIMATE] += 1
                if field[FANVARE] > 0:
                    field[FANVARE] -= 1
                    soul[FANVARE] += 1
                    hand, main_deck, _ = draw(hand, main_deck)
                    fanvare_draw = 1
            fanvare_per_turn.append(fanvare_draw)

        # Opponent's turn
        opponents_grade += 1
        ## Damage check
        for _ in range(random.choice([1,2])):
            if damage_taken == 5:
                break
            hand, main_deck, damage_check = draw(hand, main_deck, add=False)
            if damage_check == OVER:
                hand, main_deck = draw(hand, main_deck)
                break
            damage_taken += 1

    # return tuple(fanvare_per_turn + rewrites_per_turn)
    return tuple(rewrites_per_turn)

def _mulligan(hand: dict, deck: dict):
    _handsize = 5
    mulligan_range = random.sample(
        list(deck.keys()), 
        counts=list(deck.values()),
        k = _handsize*2)
    premulligan = mulligan_range[:5]
    postmulligan = mulligan_range[5:]

    card: VanguardCard
    for keep in [SENTINEL, PERSONA, ALFKNIGHTS, FANVARE]:
        if keep not in premulligan:
            continue
        hand[keep] += 1
        premulligan.remove(keep)

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1
    for card in hand:
        deck[card] -= hand[card]
    return hand, deck

def rewrite_count(data: np.array):
    turn3 = data[:, 0]
    turn4 = data[:, 1]
    turn5 = data[:, 2]
    total_rewrites = turn3 + turn4 + turn5
    return total_rewrites

def fanvares(data: np.array):
    turn3 = data[:, 0]
    turn4 = data[:, 1]
    turn5 = data[:, 2]
    total_fanvares = turn3 + turn4 + turn5
    return np.where(total_fanvares < 2, 0, 1)

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, rewrite_count)

""" Keep Fanvare in mulligan
   Normal  Fanvare  Ult Skill    Mean (Going 1st)        Mean (Going 2nd)
0      17        3          3   [0.0, 0.8086, 0.6329]   [0.7606, 0.595, 0.4959]
1      18        3          2   [0.0, 0.8056, 0.6323]   [0.7635, 0.5924, 0.4888]
2      18        2          3   [0.0, 0.809, 0.6356]    [0.7629, 0.5958, 0.4884]
3      19        2          2   [0.0, 0.8075, 0.6369]   [0.7602, 0.5888, 0.4729]
"""

""" Return Fanvare in mulligan
   Normal  Fanvare  Ult Skill    Mean (Going 1st)        Mean (Going 2nd)
0      17        3          3   [0.0, 0.8117, 0.6368]   [0.7686, 0.5993, 0.4973]
1      18        3          2   [0.0, 0.8135, 0.6387]   [0.7675, 0.5976, 0.4913]
2      18        2          3   [0.0, 0.8133, 0.6366]   [0.7681, 0.5980, 0.4884]
3      19        2          2   [0.0, 0.8127, 0.6356]   [0.7662, 0.5969, 0.4829]
"""