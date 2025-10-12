import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Ride Deck G0", 0, inRideDeck=True, max = 0)
RIDE_G1 = VanguardCard("Ride Deck G1", 1, inRideDeck=True, max = 0)
RIDE_G2 = VanguardCard("Ride Deck G2", 2, inRideDeck=True, max = 0)
RIDE_G3 = VanguardCard("Ride Deck G3", 3, inRideDeck=True, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
FRONT = VanguardCard("Soul Front", 0, trigger = True, min = 0, max = 0)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)
GATE = VanguardCard("Moon Gate", 1, unit = False, min = 1, max = 1)

NORMAL = VanguardCard("Normal Unit", 2, max = 20)
HELGVARR = VanguardCard("3rd Mythisch Helgvarr", 1, min = 4, max = 4)
MYTHISCH = VanguardCard("Mythisch", 2)

cards = [NORMAL, MYTHISCH, HELGVARR, TRIGGER, FRONT, SENTINEL, PERSONA, GATE, STARTER, RIDE_G1, RIDE_G2, RIDE_G3]

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
    while premulligan[NORMAL] > 0:
        premulligan[NORMAL] -= 1
        hand[NORMAL] += 1
    for keep in [SENTINEL, PERSONA]:
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
    
    lastTurn = 4
    myths_in_gate = []
    soul = 0
    energy = 0 if goingSecond else -3
    advantage_made = 0
    for turn in range(lastTurn):
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
                for choice in ["hand", "gate"]:
                    if HELGVARR in searchArea:
                        search_target = HELGVARR
                    elif MYTHISCH in searchArea:
                        search_target = MYTHISCH
                    else:
                        break
                    searchArea.remove(search_target)
                    main_deck.remove(search_target)
                    if choice == "hand":
                        advantage_made += 1
                        hand[search_target] += 1
                    else:
                        myths_in_gate.append(search_target)
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
        for _ in range(gate_openings):
            searchArea = main_deck[:7]
            for choice in ["hand", "gate", "gate"]:
                if HELGVARR in searchArea:
                    search_target = HELGVARR
                elif MYTHISCH in searchArea:
                    search_target = MYTHISCH
                else:
                    break
                if choice == "gate" and vanguard.grade < 3:
                    break
                searchArea.remove(search_target)
                main_deck.remove(search_target)
                if choice == "hand":
                    advantage_made += 1
                    hand[search_target] += 1
                else:
                    myths_in_gate.append(search_target)
            random.shuffle(main_deck)

        while vanguard.grade == 3 and hand[HELGVARR] > 0:
            searchArea = main_deck[:5]
            if PERSONA in searchArea:
                main_deck.remove(PERSONA)
                hand[PERSONA] += 1
            random.shuffle(main_deck)
            soul += 1
            hand[HELGVARR] -= 1

        # Battle phase
        for _ in range(2):
            if vanguard.grade != 3:
                break
            if not myths_in_gate:
                break
            call = myths_in_gate.pop()
            advantage_made += 1
            if call == HELGVARR:
                searchArea = main_deck[:5]
                if PERSONA in searchArea:
                    main_deck.remove(PERSONA)
                    hand[PERSONA] += 1
                random.shuffle(main_deck)
                soul += 1
        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = main_deck.pop()
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1
        

    return advantage_made

def Threshold(data: list):
    mu = np.mean(data)
    target = 9
    distance = -(mu - target)**2
    if mu > target:
        distance += 1
    return (distance)

veissrugr = GameEnvironment(cards, 50, RunGame, Threshold)

# 1 Myth off grade 2 search
# 1 off turn 2 Gate
# 2 off turn 3 Gate + Veiss skill
# 2 off turn 3 Veissrugr call
# 2 off turn 4 Gate + Veiss skill
# 2 off turn 4 Veissrugr call
# 2 off turn 5 Gate + Veiss skill
# 2 off turn 5 Veissrugr call