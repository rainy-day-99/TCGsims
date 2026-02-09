import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

TRIGGER = VanguardCard("Trigger", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Dragveda", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Vyrgilla cards
ALFKNIGHTS = VanguardCard("Alfknights", 3, min = 4, max = 4)
TWOS = VanguardCard("Grade 2", 2, min = 5, max = 5) # Ezerwur + Defensing Roar

# Variables
NORMAL = VanguardCard("Normal", 1)
NIRMINH = VanguardCard("Nirminh", 1, min = 3, max = 5)
FANVARE = VanguardCard("Fanvare", 3, min = 2, max = 3)
ULTIMATE = VanguardCard("Ultimate", 2, unit = False, min = 2, max = 2)

card_types = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA, 
              ALFKNIGHTS, FANVARE, ULTIMATE,
              NIRMINH, TWOS]

def run_game(main_deck: dict[VanguardCard, int], goingSecond: bool, cache = {}, debug = False):
    goingSecond = True
    # Mulligan step
    hand: dict[VanguardCard, int] = {card: 0 for card in main_deck}
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
        hand, main_deck = _draw(hand, main_deck)
        rewrite = False

        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck = _draw(hand, main_deck)
            if vanguard_grade == 3:
                if main_deck[TWOS] > 0:
                    main_deck[TWOS] -= 1
                    hand[TWOS] += 1
                elif main_deck[ULTIMATE] > 0:
                    main_deck[ULTIMATE] -= 1
                    hand[ULTIMATE] += 1
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck = _draw(hand, main_deck)

        # Main phase
        ## Use Nirminh to search for Alfknights
        while hand[NIRMINH] > 0 and vanguard_grade >= 3 and hand[ALFKNIGHTS] > 0:
            hand[NIRMINH] -= 1
            search_range = random.sample(
                            list(main_deck.keys()), 
                            counts=list(main_deck.values()),
                            k=7)
            found_card = False
            ### First, try to find cards we don't already have in order or priority
            for grade3 in [ALFKNIGHTS, PERSONA, FANVARE]:
                if hand[grade3] > 0:
                    continue
                if grade3 not in search_range:
                    continue
                main_deck[grade3] -= 1
                hand[grade3] += 1
                found_card = True
                break
            ### If we didn't add anything before, just take whatever's available
            for grade3 in [ALFKNIGHTS, PERSONA, FANVARE]:
                if found_card:
                    continue
                if grade3 not in search_range:
                    continue
                main_deck[grade3] -= 1
                hand[grade3] += 1
                found_card = True
                break
            ### Nirminh costs a counter-blast, so we only add one card a turn
            if found_card:
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
            drive_check = random.choices(list(main_deck.keys()),   
                                        weights=list(main_deck.values()), 
                                        k=1)[0]
            main_deck[drive_check] -= 1
            hand[drive_check] += 1
            if drive_check == OVER:
                hand, main_deck = _draw(hand, main_deck)
                hand[OVER] -= 1
                drives += base_drives

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
                    hand, main_deck = _draw(hand, main_deck)
                    fanvare_draw = 1
            fanvare_per_turn.append(fanvare_draw)

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
            if damage_check == OVER:
                hand, main_deck = _draw(hand, main_deck)
                break
            damage_taken += 1

    return tuple(fanvare_per_turn + rewrites_per_turn)
    # return tuple(rewrites_per_turn)

def _draw(hand: dict[VanguardCard, int], deck: dict[VanguardCard, int]):
    top_of_deck = random.choices(
        list(deck.keys()),   
        weights=list(deck.values()), k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
    hand[draw] += 1
    return hand, deck

def _mulligan(hand: dict[VanguardCard, int], deck: dict[VanguardCard, int]):
    _handsize = 5
    mulligan_range = random.sample(
        list(deck.keys()), 
        counts=list(deck.values()),
        k = _handsize*2)
    premulligan = mulligan_range[:5]
    postmulligan = mulligan_range[5:]

    card: VanguardCard
    keep_one = [SENTINEL, TWOS, ALFKNIGHTS]
    keep_all = [NIRMINH]
    for card in premulligan:
        if card in keep_all:
            premulligan.remove(card)
            hand[card] += 1
        elif (card in keep_one) and (hand[card] == 0):
            premulligan.remove(card)
            hand[card] += 1

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1
    for card in hand:
        deck[card] -= hand[card]
    return hand, deck

def rewrite_count(data: np.array):
    turn3 = data[:, 3]
    turn4 = data[:, 4]
    turn5 = data[:, 5]
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

# Fanvare T3, T4, T5, Alfknights T3, T4, T5
""" 4 Nirminh, put back Fanvare
   Normal  Fanvare  Ultimate   Score       n                                              Mean
0       5        3         3  2.0456  250000  [0.8069, 0.7828, 0.7389, 0.7425, 0.6782, 0.6249]
1       6        2         3  2.0441  250000  [0.7882, 0.6736, 0.5684, 0.7438, 0.6795, 0.6208]
2       6        3         2  2.0418  250000  [0.7881, 0.7464, 0.6858, 0.7435, 0.6783, 0.6199]
3       7        2         2  2.0402  250000  [0.7743, 0.6463, 0.5543, 0.7452, 0.6786, 0.6164]
"""

""" 4 Nirminh, keep one Fanvare
   Normal  Fanvare  Ultimate   Score       n                                              Mean
0       5        3         3  2.0279  250000  [0.8211, 0.7899, 0.7452, 0.7340, 0.6716, 0.6224]
1       6        2         3  2.0328  250000  [0.8025, 0.6893, 0.5752, 0.7374, 0.6763, 0.6191]
2       6        3         2  2.0252  250000  [0.7975, 0.7484, 0.6878, 0.7358, 0.6716, 0.6178]
3       7        2         2  2.0230  250000  [0.7831, 0.6579, 0.5595, 0.7381, 0.6727, 0.6122]
"""

"""
    34 cards
    --------
    Grade 3 (10)
    4 Alfknights
    3 Fanvare
    3 Persona Ride
    --------
    Grade 2 (10)
    4 Ezerwur
    1 Defensing Roar
    2 Ultimate Skill
    1 Regalis Piece
    1 Falhart
    1 Variance Ray Dragon
    --------
    Grade 1 (13)
    4 Sentinel
    4 Nirminh
    1 Summit Flare Dragon
    3 Shenryi
    2 Flare Cosmor
"""