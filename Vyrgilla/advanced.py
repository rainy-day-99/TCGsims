import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

""" 
    Checking effects of draw triggers
"""

TRIGGER = VanguardCard("Trigger", 0, trigger = True, min = 15, max = 15)
DRAW = VanguardCard("Flare Veil", 0, trigger = True, min = 0, max = 0)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Vyrgilla cards
EZERWUR = VanguardCard("Ezerwur", 2, min = 4, max = 4)
ALFKNIGHTS = VanguardCard("Alfknights", 3, min = 4, max = 4)
NIRMINH = VanguardCard("Nirminh", 1, min = 0, max = 0)

# Variables
NORMAL = VanguardCard("Normal Unit", 2, min = 15, max = 15)
SHENRYI = VanguardCard("Shenryi", 1, min = 0, max = 0)
FANVARE = VanguardCard("Fanvare", 3, min = 2, max = 2)
ULTIMATE = VanguardCard("Ultimate Skill", 2, unit = False, min = 2, max = 2)

card_types = [NORMAL, TRIGGER, DRAW, OVER, SENTINEL, PERSONA, 
              EZERWUR, ALFKNIGHTS, FANVARE, ULTIMATE, 
              SHENRYI, NIRMINH]

def run_game(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    # goingSecond = True

    # Mulligan step
    hand = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 5
    opponents_grade = 1 if goingSecond else 0
    
    rewrites_per_turn = []
    fanvare_per_turn = []
    drop = {FANVARE: 0, ULTIMATE: 0}
    field = {FANVARE: 0, ULTIMATE: 0, SHENRYI: 0}
    soul = {FANVARE: 0, ALFKNIGHTS: 0}
    damage_taken = 0
    for turn in range(1, last_turn + 1):      
        # Start of turn
        hand, main_deck = _draw(hand, main_deck)
        rewrite = False

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck = _draw(hand, main_deck)
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck = _draw(hand, main_deck)

        # Main phase
        ## Call Nirminh once we're on grade 3
        if hand[NIRMINH] > 0 and hand[ALFKNIGHTS] < 2 and vanguard_grade >= 3:
            hand[NIRMINH] -= 1
            search_space = random.sample(list(main_deck.keys()),   
                                        counts=list(main_deck.values()), 
                                        k=7)
            for target in [ALFKNIGHTS, PERSONA, FANVARE]:
                if target not in search_space:
                    continue
                main_deck[target] -= 1
                hand[target] += 1
                break

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

        can_fanvare_draw = False
        if opponents_grade >= 3 and hand[FANVARE] > 0 and hand[ULTIMATE] > 0:
            ## Call Fanvare, use soul-blast
            hand[FANVARE] -= 1
            field[FANVARE] += 1
            if soul[FANVARE] > 0:
                soul[FANVARE] -= 1
                drop[FANVARE] += 1
            ## Play Ultimate Skill for turn
            hand[ULTIMATE] -= 1
            drop[ULTIMATE] += 1
            can_fanvare_draw = True
        ## Call Shenryi if possible:
        field[SHENRYI] += hand[SHENRYI]
        hand[SHENRYI] = 0

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        extra_drives = 1 if rewrite else 0
        checked_dragveda = False
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives + extra_drives):
            drive_check = random.choices(list(main_deck.keys()),   
                                        weights=list(main_deck.values()), 
                                        k=1)[0]
            main_deck[drive_check] -= 1
            hand[drive_check] += 1
            if drive_check == OVER:
                hand, main_deck = _draw(hand, main_deck)
                hand[OVER] -= 1
                checked_dragveda = True
            if drive_check == DRAW:
                hand, main_deck = _draw(hand, main_deck)
        ## Dragveda drive checks
        for _ in range(drives):
            if not checked_dragveda:
                break
            drive_check = random.choices(list(main_deck.keys()),   
                                        weights=list(main_deck.values()), 
                                        k=1)[0]
            main_deck[drive_check] -= 1
            hand[drive_check] += 1
            if drive_check == DRAW:
                hand, main_deck = _draw(hand, main_deck)
        ## Use Shenryis on field
        while opponents_grade >= 1 and field[SHENRYI] > 0:
            field[SHENRYI] -= 1
            hand, main_deck = _draw(hand, main_deck)

        # End of turn
        if vanguard_grade >= 3:
            if rewrite:
                rewrites_per_turn.append(1)
            else:
                rewrites_per_turn.append(0)
            if can_fanvare_draw:
                fanvare_per_turn.append(1)
                hand, main_deck = _draw(hand, main_deck)
                field[FANVARE] -= 1
                soul[FANVARE] += 1
            else:
                fanvare_per_turn.append(0)

        # Opponent's turn
        opponents_grade += 1
        ## Damage check
        for _ in range(random.choice([1,2])):
            if damage_taken == 5:
                break
            damage_check = random.choices(list(main_deck.keys()),   
                                            weights=list(main_deck.values()), 
                                            k=1)[0]
            main_deck[damage_check] -= 1
            if damage_check == DRAW:
                hand, main_deck = _draw(hand, main_deck)
            if damage_check == OVER:
                hand, main_deck = _draw(hand, main_deck)
                break
            damage_taken += 1

    return tuple([goingSecond] + fanvare_per_turn + rewrites_per_turn)

def _draw(hand: dict, deck: dict):
    top_of_deck = random.choices(
        list(deck.keys()),   
        weights=list(deck.values()), k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
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

    card: VanguardCard
    for keep in [SENTINEL, PERSONA, ALFKNIGHTS, EZERWUR, NIRMINH, SHENRYI]:
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
    turn3 = data[:, 4]
    turn4 = data[:, 5]
    turn5 = data[:, 6]
    total_rewrites = turn3 + turn4 + turn5
    return total_rewrites

def fanvares(data: np.array):
    turn3 = data[:, 1]
    turn4 = data[:, 2]
    turn5 = data[:, 3]
    total_fanvares = turn3 + turn4 + turn5
    return np.where(total_fanvares < 2, 0, 1)

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, rewrite_count)