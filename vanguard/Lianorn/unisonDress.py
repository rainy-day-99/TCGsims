import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Blessfavor", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)

NORMAL = VanguardCard("Normal Unit", 1)
SINCERIETE = VanguardCard("Sinceriete", 1, min = 4, max = 4)
LAGRACE = VanguardCard("Lagrace", 2, min = 2, max = 4)
REGALIS = VanguardCard("Fire Regalis", 3, unit = False, min = 1, max = 1)

TRAUMEND = VanguardCard("Lianorn Traumend", 3, min = 0, max = 3)
VIVACE = VanguardCard("Lianorn Vivace", 3, min = 0, max = 4)

cards = [NORMAL, SINCERIETE, LAGRACE, TRAUMEND, VIVACE, REGALIS, SENTINEL, TRIGGER, OVER]

# Goal is to maximize the chance of A) having a Lianorn to ride turn 4, and to use the extra drive on Traumend.

# Assumptions:
# 1) Traumend > Vivace when given the choice. Generally speaking persona ride on Traumend is just better
# 2) Keep one Lianorn and Lagrace in opening mulligan, return extras. We want Lianorns, but we don't want them early
# 3) Can only use one Lagrace a turn. We can't be picky on counter-blast.
# 4) We only go for the extra drive if we have more than one Lianorn. We don't put the only G3 away for a drive
# 5) It's fine if we happen to have both a Traumend and Vivace turn 4. What we don't want are duplicates.

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
        if card in [VIVACE, TRAUMEND]:
            continue
        if card in [SENTINEL, LAGRACE] and hand[card] > 0:
            continue
        premulligan.remove(card)
        hand[card] += 1
    if TRAUMEND in premulligan:
        hand[TRAUMEND] += 1
        premulligan.remove(TRAUMEND)
    elif VIVACE in premulligan:
        hand[VIVACE] += 1
        premulligan.remove(VIVACE)
    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1

    for card in hand:
        main_deck[card] -= hand[card]
    DebugPrint("Post mulligan: " + str({card: hand[card] for card in hand if hand[card] > 0}))
    
    # This is Lianorn, we go second always :)
    goingSecond = True

    vanguard_grade = 0
    lastTurn = 4
    energy = 0 if goingSecond else -3
    opponents_grade = 1 if goingSecond else 0
    extra_drive_used = False
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[draw] -= 1
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        
        # Ride step
        energy += 3
        if vanguard_grade < 3:
            if hand[SINCERIETE] > 0:
                hand[SINCERIETE] -= 1
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Drew {draw} off of Sinceriete")
            vanguard_grade += 1
            DebugPrint(f"Rode up to grade {vanguard_grade}")
            if vanguard_grade == 1 and goingSecond:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Drew {draw} off of starter")
        else:
            if not extra_drive_used:    
                return 0
            if (hand[TRAUMEND] + hand[VIVACE]) == 0:
                return 0
            if (hand[TRAUMEND] + hand[VIVACE]) > 2:
                return 0
            return 1
        DebugPrint(hand)

        # Main phase
        if hand[REGALIS] > 0 and vanguard_grade >= 3:
            hand[REGALIS] -= 1
            DebugPrint("Played the Fire Regalis. Looking at top 5...")
            search_space = random.sample(cards, k = 5, counts=list(main_deck.values()))
            if LAGRACE in search_space and hand[LAGRACE] < 1:
                hand[LAGRACE] += 1
                main_deck[LAGRACE] -= 1
            else:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Whiffed search, drew {search_space[0]} instead")

        if hand[LAGRACE] > 0 and vanguard_grade >= 2:
            hand[LAGRACE] -= 1
            DebugPrint("Called Lagrace. Looking at top 7...")
            search_space = random.sample(cards, k = 7, counts=list(main_deck.values()))
            if TRAUMEND in search_space and (hand[TRAUMEND] + hand[VIVACE]) < 2:
                main_deck[TRAUMEND] -= 1
                hand[TRAUMEND] += 1
                DebugPrint("Added Traumend from skill")
            elif VIVACE in search_space and (hand[TRAUMEND] + hand[VIVACE]) < 2:
                main_deck[VIVACE] -= 1
                hand[VIVACE] += 1
                DebugPrint("Added Vivace from skill")
            else:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Whiffed search, drew {search_space[0]} instead")

        # Battle phase
        drives = 1 if vanguard_grade < 3 else 3
        if opponents_grade == 0:
            drives = 0
        while drives > 0:
            drives -= 1
            check = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[check] -= 1
            DebugPrint(f"Drove check {check}")
            if check != OVER:
                hand[check] += 1
            else:
                draws = random.sample(cards, counts=list(main_deck.values()), k=2)
                for card in draws:
                    hand[card] += 1
                    main_deck[card] -= 1
            if not extra_drive_used and vanguard_grade == 3 and (hand[TRAUMEND] + hand[VIVACE]) > 1:
                extra_drive_used = True
                if hand[VIVACE]:
                    hand[VIVACE] -= 1
                else:
                    hand[TRAUMEND] -= 1
                drives += 1

        # Opponent's turn
        opponents_grade += 1
        damage = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[damage] -= 1
        DebugPrint(f"Damage checked {damage}")
        if damage == OVER:
            draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[draw] -= 1
            hand[draw] += 1
    
    
def Mean(data: list):
    return np.mean(data)

lianorn = GameEnvironment(cards, 50, RunGame, Mean)