import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard
from helper import draw, debugprint

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

# Arkhite specific variables
RESEARCH = VanguardCard("Torrential Energy Research", 1, min = 4, max = 4)
MONSTER = VanguardCard("Monster Unit", 2)
NORMAL = VanguardCard("Normal Unit", 1, min = 0, max = 4)
PANTERA = VanguardCard("Pantera the Slasher", 1, min = 3, max = 3)
VALTROSSA = VanguardCard("Valtrossa&Liel", 2, min = 3, max = 3)

card_types = [NORMAL, RESEARCH, MONSTER, PANTERA, VALTROSSA,
              TRIGGER, OVER, SENTINEL, PERSONA]

def run_game(main_deck: dict[VanguardCard, int], going_second: bool, cache = {}, debug = False):
    # Mulligan step
    hand: dict[VanguardCard, int] = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    if sum(hand.values()) != 5:
        print("Hand doesn't have 5 cards!")
    if sum(main_deck.values()) != 45:
        print("Deck doesn't have 45 cards!")
    vanguard_grade = 0
    last_turn = 4
    opponents_grade = 1 if going_second else 0
    damage_taken = 0

    orders_played = 0
    monsters_researched = 0
    total_researched = 0    
    drop_monsters = 0
    for turn in range(last_turn):       
        # Start of turn
        debugprint(f"------------------- Turn {turn + 1} -------------------", debug)
        hand, main_deck, card_drawn = draw(hand, main_deck)
        debugprint(f"Drew {card_drawn} for turn", debug)
        # Ride step
        debugprint(f"# Ride step", debug)
        if vanguard_grade < 3:
            if hand[MONSTER] > 0:
                hand[MONSTER] -= 1
                drop_monsters += 1
                debugprint(f" Discarded a monster for ride cost", debug)
            vanguard_grade += 1
            debugprint(f" Rode to grade {vanguard_grade}", debug)
            
            if vanguard_grade == 1 and going_second:
                hand, main_deck, starter_draw = draw(hand, main_deck)
                debugprint(f" Drew {starter_draw} off of starter", debug)
            if vanguard_grade < 3 and main_deck[RESEARCH] > 0:
                main_deck[RESEARCH] -= 1
                hand[RESEARCH] += 1
                debugprint(f" Added Torrential Energy Research to hand", debug)
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck, persona_draw = draw(hand, main_deck)
            debugprint(f" Persona ride! Drew {persona_draw}", debug)

        debugprint(f" - Hand: {hand}", debug)
        debugprint(f" - Drop: {drop_monsters}, Orders: {orders_played}, Monsters researched: {monsters_researched}", debug)

        # Main phase
        debugprint(f"# Main phase", debug)
        if vanguard_grade >= 2 and hand[VALTROSSA] > 0:
            debugprint(f" Called Valtrossa&Liel", debug)
            hand[VALTROSSA] -= 1
            search_range = random.sample(
                population = list(main_deck.keys()),
                counts = list(main_deck.values()),
                k = 5
            )
            debugprint(f" - {search_range}", debug)
            for target in [RESEARCH, MONSTER]:
                if target not in search_range:
                    continue
                main_deck[target] -= 1
                hand[target] += 1
                break 
        if hand[PANTERA] > 0 and hand[RESEARCH] == 0 and main_deck[RESEARCH] > 0:
            debugprint(f" Called Pantera, searching for TER", debug)
            hand[PANTERA] -= 1
            main_deck[RESEARCH] -= 1
            hand[RESEARCH] += 1
        if hand[RESEARCH] > 0:
            debugprint(f" Played Torrential Energy Research for turn", debug)
            hand[RESEARCH] -= 1
            orders_played += 1
            search_range = random.sample(
                population = list(main_deck.keys()),
                counts = list(main_deck.values()),
                k = 5
            )
            debugprint(f" - TER: {search_range}", debug)
            ### Add monster to hand first
            for monster in [SENTINEL, PERSONA, MONSTER]:
                if monster not in search_range:
                    continue
                main_deck[monster] -= 1
                hand[monster] += 1
                search_range.remove(monster)
                debugprint(f" Added {monster} to hand", debug)
                break
            ### Put monster to drop last
            for monster in [PERSONA, MONSTER]:
                if monster not in search_range:
                    continue
                main_deck[monster] -= 1
                drop_monsters += 1
                debugprint(f" Dropped {monster}", debug)
                break
        debugprint(f" - Hand: {hand}", debug)
        debugprint(f" - Drop: {drop_monsters}, Orders: {orders_played}, Monsters researched: {monsters_researched}", debug)
        
        debugprint(f"# Research time!", debug)
        maximum_research = orders_played
        if vanguard_grade >= 3:
            maximum_research += 3

        discard_monsters = min(hand[MONSTER], max(maximum_research - drop_monsters, 0))
        hand[MONSTER] -= discard_monsters
        drop_monsters += discard_monsters

        research_count = min(drop_monsters, maximum_research)
        monsters_researched += research_count
        total_researched += research_count
        drop_monsters -= research_count
        debugprint(f" Researched {research_count} monsters this turn", debug)
        debugprint(f" - Hand: {hand}", debug)
        debugprint(f" - Drop: {drop_monsters}, Orders: {orders_played}, Monsters researched: {monsters_researched}", debug)
       
        debugprint(f"# Battle phase", debug)
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
            debugprint(f" No drive checks", debug)
        for _ in range(drives):
            hand, main_deck, drive_check = draw(hand, main_deck)
            debugprint(f" Drove check {drive_check}", debug)

        ## Assuming we called monsters during battle and used Arkhite's skill,
        ## we dump all monsters researched into the drop to use again
        if vanguard_grade >= 3:
            drop_monsters += monsters_researched
            monsters_researched = 0 

        # Opponent's turn
        debugprint(f"#", debug)
        debugprint(f" - Cumulative research: {total_researched}", debug)
        opponents_grade += 1
        for _ in range(random.choice([1, 2])):
            if damage_taken == 5:
                break
            hand, main_deck, damage = draw(hand, main_deck, add=False)
            if damage == OVER:
                break
            damage_taken += 1
    
    return (going_second, total_researched)

def _mulligan(hand: dict[VanguardCard, int], deck: dict[VanguardCard, int]):
    _handsize = 5
    _put_all_back = False
    card: VanguardCard
    _mulligan_range = random.sample(
        population=list(deck.keys()), 
        counts=list(deck.values()),
        k = _handsize * 2)
    for _ in range(_handsize):
        hand[_mulligan_range.pop()] += 1

    _returned = hand[TRIGGER]
    hand[TRIGGER] = 0
    # Keep one
    for keep in [PERSONA, PANTERA, VALTROSSA]:
        if hand[keep] <= 1:
            continue
        _returned += hand[keep] - 1
        hand[keep] = 1
    # Optional: put all monsters back to deck.
    if _put_all_back:
        _returned += hand[MONSTER]
        hand[MONSTER] = 0

    for _ in range(_returned):
        hand[_mulligan_range.pop()] += 1
    for card in hand:
        deck[card] -= hand[card]
    return hand, deck

def value(data: np.array):
    return data[:, 1]

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, value)