import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

maxDeckSize = 50

STARTER = VanguardCard("V Starter", 0, inRideDeck=True, min = 1, max = 1)
TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
BRANWEN = VanguardCard("Branwen", 1, min = 4, max = 4)
GRADE_1 = VanguardCard("G1", 1)
GRADE_2 = VanguardCard("G2", 2)
GRADE_3 = VanguardCard("G3", 3)
ORDER = VanguardCard("Order", 1, unit = False, min = 2, max = 2)

def RunGame(deck: list[VanguardCard], hand: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)

    vanguard = deck.pop()

    random.shuffle(deck)
    startingHandSize = 5
    premulligan = {card: 0 for card in hand}
    for _ in range(startingHandSize):
        premulligan[deck.pop()] += 1
    DebugPrint(f"Premulligan: {premulligan}")
    if premulligan[BRANWEN] > 0:
        premulligan[BRANWEN] -= 1
        hand[BRANWEN] += 1
    for grade in [1,2,3]:
        for card in premulligan:
            if premulligan[card] == 0:
                continue
            if card.grade != grade:
                continue
            if hand[card] > 0:
                continue
            if card.grade == 1 and hand[BRANWEN] > 0:
                continue
            if not card.isUnit:
                continue
            premulligan[card] -= 1
            hand[card] += 1
            break
    cardsPutBack = []
    for card in premulligan:
        cardsPutBack += [card] * premulligan[card]
    DebugPrint(f"Putting back {cardsPutBack}")
    for i in cardsPutBack:
        hand[deck.pop()] += 1
    deck += cardsPutBack
    random.shuffle(deck)
    DebugPrint(f"Post mulligan: {hand}")
    
    lastTurn = 3
    usedGAssist = True
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = deck.pop()
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        next_grade = vanguard.grade + 1
        rideTarget = []
        card: VanguardCard
        DebugPrint(hand)
        for card in hand:
            if hand[card] == 0:
                continue
            if card.grade != next_grade:
                continue
            if not card.isUnit:
                continue
            rideTarget.append(card)
            hand[card] -= 1
            break
        if not rideTarget and not usedGAssist:
            usedGAssist = True
            top5 = deck[:5]
            for card in top5:
                if card.grade != next_grade:
                    continue
                if not card.isUnit:
                    continue
                deck.remove(card)
                rideTarget.append(card)
                break
            random.shuffle(deck)
        if rideTarget:
            vanguard = rideTarget.pop()
            DebugPrint(f"Rode {vanguard}")
            if vanguard.grade == 1:
                starter_draw = deck.pop()
                DebugPrint(f"Drew {starter_draw} off of starter")
                hand[starter_draw] += 1
            if vanguard.grade == 3:
                return 1
            if vanguard == BRANWEN:
                top5 = deck[:5]
                if GRADE_3 in top5:
                    deck.remove(GRADE_3)
                    hand[GRADE_3] += 1
                random.shuffle(deck)
        else:
            DebugPrint("Missed ride")

        # Main phase
        while hand[BRANWEN] > 0:
            hand[BRANWEN] -= 1
            top5 = deck[:5]
            if GRADE_3 in top5:
                deck.remove(GRADE_3)
                hand[GRADE_3] += 1
            random.shuffle(deck)

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = deck.pop()
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1

    return 0

def Mean(data: list):
    p = np.mean(data)
    return p

premium = GameEnvironment([TRIGGER, BRANWEN, GRADE_1, GRADE_2, GRADE_3, STARTER], 
                          50, RunGame, Mean)