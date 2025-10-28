import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard


TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

WOLF = VanguardCard("First Mythisch Roztnir", 2, min = 4, max = 4)
SNAKE = VanguardCard("Second Mythisch Garzorms", 2,  min = 4, max = 4)
HEL = VanguardCard("Third Mythisch Helgvarr", 1, min = 4, max = 4)

CROW = VanguardCard("Mythisch Ravnarowg", 2, min = 5, max = 7)
LUNARITE = VanguardCard("Lunarite", 3, unit = False, min = 4, max = 8)
NORMAL = VanguardCard("Normal Unit", 3, unit = False)

cards = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA,
         WOLF, SNAKE, HEL, CROW, LUNARITE]

def RunGame(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)
    
    startingHandSize = 5
    cards = list(main_deck.keys())
    mulligan_range = random.sample(cards, k = startingHandSize * 2, counts=list(main_deck.values()))
    premulligan = mulligan_range[:5]
    postmulligan = mulligan_range[5:]
    DebugPrint(f"\nPremulligan: {premulligan}")
    
    # Mulligan step
    hand = {card: 0 for card in main_deck}
    card: VanguardCard
    for card in premulligan:
        if card.isTrigger:
            continue
        if card in [SNAKE, CROW]:
            continue
        if hand[card] > 0:
            continue
        premulligan.remove(card)
        hand[card] += 1

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1

    for card in hand:
        main_deck[card] -= hand[card]
    DebugPrint("Post mulligan: " + str({card: hand[card] for card in hand if hand[card] > 0}))
    
    vanguard_grade = 0
    lastTurn = 4
    energy = 0 if goingSecond else -3
    opponents_grade = 1 if goingSecond else 0

    moon_gate = []
    bottom_deck = []
    drop = []
    lunarites_played = 0
    soul = 0
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[draw] -= 1
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        energy += 3
        if vanguard_grade < 3:
            for myth in [SNAKE, CROW, WOLF, HEL]:
                if hand[myth] == 0:
                    continue
                drop.append(myth)
                hand[myth] -= 1
                break
            vanguard_grade += 1
            soul += 1
            DebugPrint(f"Rode up to grade {vanguard_grade}")
            if vanguard_grade == 1 and goingSecond:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Drew {draw} off of starter")
            if vanguard_grade == 2:
                search_area = random.sample(cards, counts=list(main_deck.values()), k=7)
                for myth in [HEL, WOLF, CROW, SNAKE]:
                    if myth not in search_area:
                        continue
                    hand[myth] += 1
                    search_area.remove(myth)
                    main_deck[myth] -= 1
                    break
                for myth in [SNAKE, CROW, WOLF, HEL]:
                    if myth not in search_area:
                        continue
                    main_deck[myth] -= 1
                    moon_gate.append(myth)
                    break
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            soul += 1
            draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[draw] -= 1
            hand[draw] += 1
            DebugPrint(f"Persona ride! Drew {draw}")
        DebugPrint(hand)

        # Main phase
        gate_openings = 0
        if energy >= 3 and vanguard_grade >= 2:
            gate_openings += 1
            energy -= 3
        if soul >= 2 and vanguard_grade == 3:
            gate_openings += 1
            energy -= 3

        while vanguard_grade == 3 and hand[HEL] > 0:
            hand[HEL] -= 1
            search_area = random.sample(cards, counts=list(main_deck.values()), k=5)
            if PERSONA in search_area and hand[PERSONA] == 0:
                hand[PERSONA] += 1
                main_deck[PERSONA] -= 1
            elif LUNARITE in search_area:
                hand[LUNARITE] += 1
                main_deck[LUNARITE] -= 1
            elif PERSONA in search_area:
                hand[PERSONA] += 1
                main_deck[PERSONA] -= 1
            soul += 1
            while bottom_deck:
                main_deck[bottom_deck.pop()] += 1

        for _ in range(gate_openings):
            search_area = random.sample(cards, counts=list(main_deck.values()), k=7)
            called_helgvarr = False
            for myth in [HEL, WOLF, CROW, SNAKE]:
                if myth not in search_area:
                    continue
                hand[myth] += 1
                search_area.remove(myth)
                main_deck[myth] -= 1
                if myth == HEL:
                    called_helgvarr = True
                break
            for _ in range(2):
                if vanguard_grade < 3:
                    break
                for myth in [SNAKE, CROW, WOLF, HEL]:
                    if myth not in search_area:
                        continue
                    main_deck[myth] -= 1
                    search_area.remove(myth)
                    moon_gate.append(myth)
                    break
            while bottom_deck:
                main_deck[bottom_deck.pop()] += 1
            if called_helgvarr:
                hand[HEL] -= 1
                search_area = random.sample(cards, counts=list(main_deck.values()), k=5)
                if PERSONA in search_area and hand[PERSONA] == 0:
                    hand[PERSONA] += 1
                    main_deck[PERSONA] -= 1
                elif LUNARITE in search_area:
                    hand[LUNARITE] += 1
                    main_deck[LUNARITE] -= 1
                elif PERSONA in search_area:
                    hand[PERSONA] += 1
                    main_deck[PERSONA] -= 1
                soul += 1
        if vanguard_grade == 3 and hand[LUNARITE] > 0:
            hand[LUNARITE] -= 1
            lunarites_played += 1
        # Battle phase
        drives = 1 if vanguard_grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            check = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[check] -= 1
            hand[check] += 1
            DebugPrint(f"Drove check {check}")

        # Opponent's turn
        for _ in range(2):
            if vanguard_grade < 3:
                break
            if (hand[SNAKE] + hand[WOLF] + hand[HEL] + hand[WOLF]) == 0:
                break
            for myth_to_bottom in [SNAKE, WOLF, HEL, CROW]:
                if myth_to_bottom not in drop:
                    continue
                bottom_deck.append(myth_to_bottom)
                drop.remove(myth_to_bottom)
                break
            for myth_to_guard in [SNAKE, WOLF, CROW, HEL]:
                hand[myth_to_guard] -= 1
                drop.append(myth_to_guard)
                break

        opponents_grade += 1
        damage = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[damage] -= 1
        DebugPrint(f"Damage checked {damage}")

    return lunarites_played

def Threshold(data: np.array):
    mu = np.mean(data)
    return mu - 2

veissrugr = GameEnvironment(cards, 50, RunGame, Threshold)