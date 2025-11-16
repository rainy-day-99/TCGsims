import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
RESEARCH = VanguardCard("Torrential Energy Research", 1, unit = False, min = 4, max = 4)
PERSONA = VanguardCard("Arkhite", 3, min = 3, max = 3)
SENTINEL = VanguardCard("Girgrand", 1, min = 4, max = 4)

# Variables
MAGNIDES = VanguardCard("Magnides", 2, max = 4)
PANTERA = VanguardCard("Pantera the Slasher", 1, max = 4)
MONSTER = VanguardCard("Monster Unit", 2)

card_types = [TRIGGER, RESEARCH, PERSONA, SENTINEL,
               MAGNIDES, MONSTER, PANTERA]

def run_game(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    # Mulligan step
    hand = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    
    vanguard_grade = 0
    last_turn = 4
    opponents_grade = 1 if goingSecond else 0

    orders_played = 0
    drop_monsters = 0
    monsters_researched = 0
    energy = -3
    field = []
    for turn in range(1, last_turn + 1):        
        # Start of turn
        hand, main_deck = _draw(hand, main_deck)
        energy += 3
        # Ride step
        if vanguard_grade < 3:
            vanguard_grade += 1
            ## Discarding for ride cost
            if hand[MONSTER] > 0:
                hand[MONSTER] -= 1
                drop_monsters += 1
            ## We draw before searching, hoping to draw a duplicate research
            if vanguard_grade == 1 and goingSecond:
                hand, main_deck = _draw(hand, main_deck)
                energy += 3
            if vanguard_grade < 3 and main_deck[RESEARCH]:
                main_deck[RESEARCH] -= 1
                hand[RESEARCH] += 1
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck = _draw(hand, main_deck)

        # Main phase
        if energy >= 9:
            energy -= 7
            hand, main_deck = _draw(hand, main_deck)

        played_research = False
        if hand[RESEARCH]: 
            played_research = True
            hand[RESEARCH] -= 1
        elif hand[PANTERA] and main_deck[RESEARCH]:
            played_research = True
            hand[PANTERA] -= 1
            main_deck[RESEARCH] -= 1

        if played_research:
            orders_played += 1
            search_area = random.sample(
                list(main_deck.keys()), 
                counts=list(main_deck.values()),
                k = 5)
            for monster in [SENTINEL, PERSONA, MAGNIDES, MONSTER]:
                if monster not in search_area:
                    continue
                search_area.remove(monster)
                main_deck[monster] -= 1
                hand[monster] += 1
                break
            for monster in [MONSTER, MAGNIDES, PERSONA]:
                if monster not in search_area:
                    continue
                main_deck[monster] -= 1
                drop_monsters += 1
                break

        ## Putting monsters into the order zone
        additional_research = 0
        if vanguard_grade >= 3 and energy >= 2:
            additional_research = 3
            energy -= 2
        _monsters_to_research = min(drop_monsters, orders_played + additional_research)
        monsters_researched += _monsters_to_research
        drop_monsters -= _monsters_to_research

        ## Calling Magnides if possible
        while hand[MAGNIDES] > 0 and vanguard_grade >= 2 and played_research:
            hand[MAGNIDES] -= 1
            field.append(MAGNIDES)
            drop_monsters += 1
            search_area = random.sample(
                list(main_deck.keys()), 
                counts=list(main_deck.values()),
                k = 5)
            if RESEARCH in search_area:
                hand[RESEARCH] += 1
                main_deck[RESEARCH] -= 1
            elif MONSTER in search_area:
                main_deck[MONSTER] -= 1
                field.append(MONSTER)

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck = _draw(hand, main_deck)

        # Opponent's turn
        if vanguard_grade >= 3:
            ## Completely empty the order zone
            drop_monsters += monsters_researched
            ## Any Monsters called to (RC) are called over
            drop_monsters += field.__len__()
            field = []
            ## Dump all extra monsters in hand
            drop_monsters += hand[MONSTER]
            hand[MONSTER] = 0
        opponents_grade += 1

        # Damage check
        hand, main_deck = _draw(hand, main_deck, False)

    return (goingSecond, monsters_researched)

def _draw(hand_cards: dict, deck: dict, add: bool = True):
    top_of_deck = random.choices(
        list(deck.keys()),   
        weights=list(deck.values()), k=1)
    draw = top_of_deck[0]
    deck[draw] -= 1
    if add:
        hand_cards[draw] += 1
    return hand_cards, deck

def _mulligan(hand_cards: dict, deck: dict):
    _handsize = 5
    mulligan_range = random.sample(
        list(deck.keys()), 
        counts=list(deck.values()),
        k = _handsize*2)
    premulligan = mulligan_range[:_handsize]
    postmulligan = mulligan_range[_handsize:]
    card: VanguardCard
    for card in premulligan:
        if card.isTrigger:
            continue
        if card == MONSTER:
            continue
        elif hand_cards[card] > 0:
            continue
        premulligan.remove(card)
        hand_cards[card] += 1

    for i, _ in enumerate(premulligan):
        hand_cards[postmulligan[i]] += 1
    for card in hand_cards:
        deck[card] -= hand_cards[card]
    return hand_cards, deck

def value(data: np.array):
    researches = data[:, 1]
    return researches

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, value)