import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Ride Deck G0", 0, max = 0)
RIDE_G1 = VanguardCard("Ride Deck G1", 1, max = 0)
RIDE_G2 = VanguardCard("Ride Deck G2", 2, max = 0)
RIDE_G3 = VanguardCard("Ride Deck G3", 3, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
FRONT = VanguardCard("Soul Front", 0, trigger = True, min = 0, max = 0)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)
GATE = VanguardCard("Moon Gate", 1, unit = False, min = 1, max = 1)

NORMAL = VanguardCard("Normal Unit", 2)
ROZTNIR = VanguardCard("Mythisch Roztnir", 2, min = 8, max = 8)
BIRD = VanguardCard("Mythisch", 2)
BOBALMINE = VanguardCard("Bobalmine", 1)

cards = [NORMAL, ROZTNIR, BIRD, STARTER, RIDE_G1, RIDE_G2, RIDE_G3, TRIGGER, FRONT, SENTINEL, PERSONA, GATE, BOBALMINE]

def RunGame(main_deck: list[VanguardCard], hand: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)
    if np.sum([1 for card in main_deck if card.isTrigger]) != 16:
        return 0
    ride_deck = [RIDE_G3, RIDE_G2, RIDE_G1, STARTER]
    if len(ride_deck) != 4:
        print("Ride deck not full!")
        return(0)
    vanguard = ride_deck.pop()

    random.shuffle(main_deck)
    startingHandSize = 5
    premulligan = {card: 0 for card in hand}
    for _ in range(startingHandSize):
        premulligan[main_deck.pop()] += 1
    DebugPrint(f"Premulligan: {premulligan}")
    
    # Mulligan step
    # while premulligan[NORMAL] > 0:
    #     premulligan[NORMAL] -= 1
    #     hand[NORMAL] += 1
    for keep in [NORMAL, SENTINEL, PERSONA, BOBALMINE]:
        if premulligan[keep] > 0:
            premulligan[keep] -= 1
            hand[keep] += 1

    cardsPutBack = []
    for card in premulligan:
        cardsPutBack += [card] * premulligan[card]
    DebugPrint(f"Putting back {cardsPutBack}")
    for _ in cardsPutBack:
        hand[main_deck.pop()] += 1
    main_deck += cardsPutBack
    random.shuffle(main_deck)
    DebugPrint(f"Post mulligan: {hand}")
    
    number_of_turns = 5
    myths_in_gate = []
    soul = 0
    energy = 0 if goingSecond else -3
    total_power = 0

    damage = []
    counterblast = 0

    for turn in range(number_of_turns):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = main_deck.pop()
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        energy += 3
        if ride_deck:
            vanguard = ride_deck.pop()
            soul += 1
            DebugPrint(f"Rode {vanguard}")
            if vanguard.grade == 1:
                if hand[GATE]:
                    hand[GATE] -= 1
                    hand[main_deck.pop()] += 1
                else:
                    main_deck.remove(GATE)
                    random.shuffle(main_deck)
                if goingSecond:
                    hand[main_deck.pop()] += 1
            if vanguard.grade == 2:
                searchArea = main_deck[:7]
                myths_found = 0
                myths_max = 2
                for card in searchArea:
                    if "Mythisch" not in card.name:
                        continue
                    if myths_found == myths_max:
                        break
                    main_deck.remove(card)
                    if myths_found == 0:
                        total_power += 10 
                        if card == ROZTNIR:
                            total_power += 5
                    else:
                        myths_in_gate.append(card)
                    myths_found += 1
                random.shuffle(main_deck)
        elif hand[PERSONA] > 0:
            soul += 1
            hand[PERSONA] -= 1
            hand[main_deck.pop()] += 1
        DebugPrint(hand)

        # Main phase
        gate_openings = 0
        if vanguard.grade >= 2 and energy >= 3:
            energy -= 3
            gate_openings += 1
        if vanguard.grade == 3 and soul >= 2:
            soul -= 2
            gate_openings += 1
        modifier = 0
        if hand[NORMAL] and vanguard.grade == 3 and counterblast > 0:
            hand[NORMAL] -= 1
            counterblast -= 1
            modifier = 10
        for _ in range(gate_openings):
            searchArea = main_deck[:7]
            myths_max = 3 if vanguard.grade == 3 else 1
            myths_found = 0
            for card in searchArea:
                if myths_found == myths_max:
                    break
                if "Mythisch" not in card.name:
                    continue
                main_deck.remove(card)
                if myths_found == 0:
                    total_power += 10 + modifier
                    if card == ROZTNIR:
                        total_power += 5
                else:
                    myths_in_gate.append(card)
                myths_found += 1
            random.shuffle(main_deck)

        # Battle phase
        if hand[BOBALMINE] > 0 and counterblast < len(damage):
            soul += 1
            hand[BOBALMINE] -= 1
            counterblast += 1
        if vanguard.grade == 3 and counterblast > 0:
            counterblast -= 1
            for _ in range(2):
                if not myths_in_gate:
                    break
                mid_battle = myths_in_gate.pop()
                total_power += 10 + modifier
                if mid_battle != ROZTNIR:
                    continue
                total_power += 5
                if counterblast > 0:
                    counterblast -= 1
                    total_power += 10

        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = main_deck.pop()
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1
        while vanguard.grade == 3 and hand[FRONT] > 0:
            soul += 1
            hand[FRONT] -= 1

        attacks = 1 if random.random() > (turn + 1)/6 else 2
        for _ in range(attacks):
            if len(damage) == 5:
                break
            damage_check = main_deck.pop()
            damage.append(damage_check)
            counterblast += 1

    return total_power

def Mean(data: list):
    mu = np.mean(data)
    return mu

veissrugr = GameEnvironment(cards, 50, RunGame, Mean)

# With 4 soul fronts:
# 203.2446
# ['Normal Unit: 5', 'Mythisch Roztnir: 8', 'Mythisch: 11', 'Trigger Unit: 12', 'Soul Front: 4', 'Perfect Guard: 4', 'Persona Ride: 3', 'Moon Gate: 1', 'Bobalmine: 2']

# Without soul fronts:
# 197.7698
#  ['Normal Unit: 5', 'Mythisch Roztnir: 8', 'Mythisch: 10', 'Trigger Unit: 16', 'Perfect Guard: 4', 'Persona Ride: 3', 'Moon Gate: 1', 'Bobalmine: 3']
