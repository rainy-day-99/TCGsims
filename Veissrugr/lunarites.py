import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

WOLF = VanguardCard("1st Mythisch Roztnir", 2, min = 4, max = 4)
SNAKE = VanguardCard("2nd Mythisch Garzorms", 2, min = 4, max = 4)
HEL = VanguardCard("3rd Mythisch Helgvarr", 1, min = 4, max = 4)
BIRD = VanguardCard("Mythisch Ravnarowg", 2, min = 7, max = 7)
GATE = VanguardCard("Moon Gate", 1, min = 1, max = 1)

# Variables
LUNARITE = VanguardCard("Lunarite Order", 3, unit=False, max = 4)
NORMAL = VanguardCard("Normal Unit", 2)

card_types = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA,
            WOLF, SNAKE, HEL, BIRD, LUNARITE, GATE]

def run_game(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    goingSecond = False
    # Mulligan step
    hand = {card: 0 for card in main_deck}
    hand, main_deck = _mulligan(hand, main_deck)
    for card in hand:
        main_deck[card] -= hand[card]
    
    vanguard_grade = 0
    last_turn = 3
    opponents_grade = 1 if goingSecond else 0
    moon_gate = []
    advantage = 0
    field = []
    bottom = []
    soul = 0
    energy = 0
    for turn in range(1, last_turn + 1):        
        persona_rode = False

        # Start of turn
        hand, main_deck = _draw(hand, main_deck)
        energy += 3
        # Ride step
        if vanguard_grade < 3:
            soul += 1
            vanguard_grade += 1
            if vanguard_grade == 1:
                if main_deck[GATE]:
                    main_deck[GATE] -= 1
                elif hand[GATE]:
                    hand[GATE] -= 1
                    hand, main_deck = _draw(hand, main_deck)
                if goingSecond:
                    hand, main_deck = _draw(hand, main_deck)
                    energy += 3
            if vanguard_grade == 2:
                moon_gate, main_deck, call = _open_gate(moon_gate, main_deck, 1)
                if call != NORMAL:
                    hand[call] += 1
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand, main_deck = _draw(hand, main_deck)
            soul += 1
            persona_rode = True

        # Main phase
        gate_openings = 0
        if soul >= 2 and vanguard_grade >= 3:
            soul -= 2
            gate_openings += 1
        if energy >= 6 and vanguard_grade >= 2:
            # Leaving 3 energy for a Helgvarr search
            energy -= 3
            gate_openings += 1

        while hand[HEL] > 0:
            if vanguard_grade < 3:
                break
            field.append(HEL)
            hand[HEL] -= 1
            if persona_rode and energy >= 3:
                energy -= 3
                hand[LUNARITE] += 1
                main_deck[LUNARITE] -= 1
            else:
                hand, main_deck = _helgvarr_search(hand, main_deck)
            while bottom:
                main_deck[bottom.pop()] += 1
        for _ in range(gate_openings):
            cards_to_gate = 2 if vanguard_grade >= 3 else 1
            moon_gate, main_deck, call = _open_gate(moon_gate, main_deck, cards_to_gate)
            if call != NORMAL:
                field.append(call)
                if call == HEL:
                    if persona_rode and energy >= 3:
                        energy -= 3
                        hand[LUNARITE] += 1
                        main_deck[LUNARITE] -= 1
                    else:
                        hand, main_deck = _helgvarr_search(hand, main_deck)
            while bottom:
                main_deck[bottom.pop()] += 1
        if hand[LUNARITE] and vanguard_grade >= 3:
            hand[LUNARITE] -= 1
            advantage += 1
        # Battle phase                
        for card in field:
            if vanguard_grade < 3:
                break
            if card != HEL:
                continue
            soul += 1
            field.remove(card)
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            hand, main_deck = _draw(hand, main_deck)
        for _ in range(2):
            if vanguard_grade < 3:
                break
            if not moon_gate:
                break
            call = moon_gate.pop()
            if call == HEL:
                soul += 1
        # Opponent's turn
        opponents_grade += 1
        hand, main_deck = _draw(hand, main_deck, False)
        if vanguard_grade >= 3:
            bottom += [BIRD, BIRD]
    return (goingSecond, advantage, hand[LUNARITE])

def _draw(hand: dict, deck: dict, add: bool = True):
    try:
        top_of_deck = random.choices(
            list(deck.keys()),   
            weights=list(deck.values()), k=1)
    except ValueError:
        return hand, deck
    draw = top_of_deck[0]
    deck[draw] -= 1
    if add:
        hand[draw] += 1
    return hand, deck

def _mulligan(hand: dict, deck: dict):
    _handsize = 5
    mulligan_range = random.sample(list(deck.keys()), 
                                    counts=list(deck.values()),
                                    k = _handsize*2)
    premulligan = mulligan_range[:5]
    postmulligan = mulligan_range[5:]
    for card in [SENTINEL, PERSONA, LUNARITE, WOLF, HEL]:
        if card in premulligan:
            premulligan.remove(card)
            hand[card] += 1

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1
    for card in hand:
        deck[card] -= hand[card]
    return hand, deck

def _open_gate(gate: list, deck: dict, to_gate: int):
    deck_size = np.sum(list(deck.values()))
    search_space = random.sample(list(deck.keys()), 
                    counts=list(deck.values()),
                    k = min(deck_size, 7))
    call = NORMAL
    number_of_mythisch = 0
    for card in search_space:
        if "Mythisch" in card.name:
            number_of_mythisch += 1
    mythisch_to_take = min(1 + to_gate, number_of_mythisch)
    for myth in [HEL, WOLF, BIRD, SNAKE]:
        if myth not in search_space:
            continue
        search_space.remove(myth)
        deck[myth] -= 1
        call = myth
        break
    for _ in range(to_gate):
        for myth in [SNAKE, WOLF, BIRD, HEL]:
            if myth not in search_space:
                continue
            search_space.remove(myth)
            deck[myth] -= 1
            gate.append(myth)
            break
    deck_size_after = np.sum(list(deck.values()))
    if deck_size_after != deck_size - mythisch_to_take:
        raise Exception("Wrong number of Mythisch taken out of deck!")
    return(gate, deck, call)

def _helgvarr_search(hand: dict, deck: dict):
    search_space = random.sample(list(deck.keys()), 
        counts=list(deck.values()),
        k = min(5, np.sum(list(deck.values()))))
    if PERSONA in search_space and hand[PERSONA] == 0:
        hand[PERSONA] += 1
        deck[PERSONA] -= 1
    elif LUNARITE in search_space:
        hand[LUNARITE] += 1
        deck[LUNARITE] += 1
    elif PERSONA in search_space:
        hand[PERSONA] += 1
        deck[PERSONA] -= 1
    return(hand, deck)

def value(data: np.array):
    orders_played = data[:, 1]
    extra_in_hand = data[:, 2]
    return (orders_played - extra_in_hand)

"""
    Always ensure that the game environment variable 
    is called 'game' so main.py can see it
"""
game = GameEnvironment(card_types, 50, run_game, value)