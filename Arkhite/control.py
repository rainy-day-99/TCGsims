import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Arkhite specific variables
RESEARCH = VanguardCard("Torrential Energy Research", 1, min = 4, max = 4)
MONSTER = VanguardCard("Monster Unit", 2)
NORMAL = VanguardCard("Normal Unit", 1, max = 0)

card_types = [NORMAL, RESEARCH, TRIGGER, OVER, SENTINEL, PERSONA]

def run_game(main_deck: dict[VanguardCard, int], going_second: bool, cache = {}, debug = False):
    # Mulligan step
    hand: dict[VanguardCard, int] = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 4
    opponents_grade = 1 if going_second else 0
    damage_taken = 0
    order_zone = {
        'orders_played': 0,
        'monsters_researched': 0,
        'total_researched': 0
    }
    drop_monsters = 0
    for _ in range(last_turn):        
        # Start of turn
        hand, main_deck, _ = draw(hand, main_deck)

        # Ride step
        if vanguard_grade < 3:
            if hand[MONSTER] > 0:
                hand[MONSTER] -= 1
                drop_monsters += 1
            vanguard_grade += 1
            if vanguard_grade == 1 and going_second:
                hand, main_deck, _ = draw(hand, main_deck)
            if vanguard_grade < 3 and main_deck[RESEARCH] > 0:
                main_deck[RESEARCH] -= 1
                hand[RESEARCH] += 1

        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck, _ = draw(hand, main_deck)

        # Main phase
        order_played = False
        ## Play an order if possibe
        if hand[RESEARCH] > 0:
            order_played = True
            hand[RESEARCH] -= 1
            order_zone['orders_played'] += 1
            search_range = random.sample(
                population = list(main_deck.keys()),
                counts = list(main_deck.values()),
                k = 5
            )
            ### Add monster to hand first
            for monster in [PERSONA, SENTINEL, MONSTER]:
                if monster not in search_range:
                    continue
                main_deck[monster] -= 1
                hand[monster] += 1
                search_range.remove(monster)
            ### Put monster to drop last
            for monster in [PERSONA, MONSTER]:
                if monster not in search_range:
                    continue
                main_deck[monster] -= 1
                drop_monsters += 1
        ## For each research order, put a monster from drop into order zone
        ## If at grade 3, increase that amount by 3 using Arkhite's ability
        arkhite_skill = 0 if vanguard_grade < 3 else 3
        monsters_to_research = max(drop_monsters, order_zone["orders_played"] + arkhite_skill)
        order_zone["monsters_researched"] += monsters_to_research
        order_zone["total_researched"] += monsters_to_research
        drop_monsters -= monsters_to_research

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck, _ = draw(hand, main_deck)
        ## Assuming we called monsters during battle and used Arkhite's skill,
        ## we dump all monsters researched into the drop to use again
        drop_monsters += order_zone["monsters_researched"]
        order_zone["monsters_researched"] = 0 

        # Opponent's turn
        opponents_grade += 1
        for _ in range(random.choice([1, 2])):
            if damage_taken == 5:
                break
            hand, main_deck, damage = draw(hand, main_deck, add=False)
            if damage == OVER:
                break
            damage_taken += 1

    return (going_second, order_zone["total_researched"])

def _mulligan(hand: dict[VanguardCard, int], deck: dict[VanguardCard, int]):
    _handsize = 5
    card: VanguardCard
    _mulligan_range = random.sample(
        population=list(deck.keys()), 
        counts=list(deck.values()),
        k = _handsize * 2)
    for _ in range(_handsize):
        hand[_mulligan_range.pop()] += 1
    _returned = []
    for card in hand:
        if card.isTrigger:
            _returned += hand[card] * [card]
            hand[card] = 0

    for _ in range(len(_returned)):
        hand[_mulligan_range.pop()] += 1
    for card in hand:
        deck[card] -= 1
    return hand, deck

def value(data: np.array):
    return data[:, 1]

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, value)