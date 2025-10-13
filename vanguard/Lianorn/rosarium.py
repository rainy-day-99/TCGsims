import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Blessfavor", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)

NORMAL = VanguardCard("Normal Unit", 1)
ROSARIUM = VanguardCard("Rosarium / Mollmoire", 1, min = 4, max = 8)

REGALIS = VanguardCard("Fire Regalis", 3, unit = False, min = 1, max = 1)
SINCERIETE = VanguardCard("Sinceriete", 1, min = 4, max = 4)
LAGRACE = VanguardCard("Lagrace", 2, min = 4, max = 4)
TRAUMEND = VanguardCard("Lianorn Traumend", 3, min = 3, max = 3)
VIVACE = VanguardCard("Lianorn Vivace", 3, min = 2, max = 2)

cards = [NORMAL, SINCERIETE, ROSARIUM, LAGRACE, TRAUMEND, VIVACE, REGALIS, SENTINEL, TRIGGER, OVER]

# Using the setup of unisonDress.py, how many Rosarium Fairies and Mollmoire do we need?
# We need at least one Rosarium on turn 3, two is fine, but three or more are unnecessary

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
        if card.grade in [VIVACE, TRAUMEND]:
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
    lastTurn = 3
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
        elif (hand[VIVACE] + hand[TRAUMEND]) > 0:
            draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[draw] -= 1
            hand[draw] += 1
            DebugPrint(f"Drew {draw} from reride")
        DebugPrint(hand)

        # Main phase
        if hand[REGALIS] > 0 and vanguard_grade >= 3:
            hand[REGALIS] -= 1
            DebugPrint("Played the Fire Regalis. Looking at top 5...")
            search_space = random.sample(cards, k = 5, counts=list(main_deck.values()))
            if ROSARIUM in search_space:
                hand[ROSARIUM] += 1
                main_deck[ROSARIUM] -= 1
            elif LAGRACE in search_space and hand[LAGRACE] < 1:
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

        if turn + 1 == lastTurn:
            if hand[ROSARIUM] == 2:
                return 1
            return 0

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
    
def Threshold(data: list):
    target = 2
    distance = abs(target - np.mean(data))
    score = 10**(-distance)
    return score

def Mean(data: list):
    return np.mean(data)

lianorn = GameEnvironment(cards, 50, RunGame, Mean)