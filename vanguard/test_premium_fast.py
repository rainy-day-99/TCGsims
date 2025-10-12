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
    goingSecond = True
    vanguard = deck.pop()

    top5 = random.sample(deck, 5)
    for card in top5:
        hand[card] += 1
        deck.remove(card)
    DebugPrint(f"Premulligan: {hand}")
    cardsToReturn = [TRIGGER] * hand[TRIGGER]
    for grade in [1,2,3]:
        for card in hand:
            if hand[card] == 0:
                continue
            if card.grade != grade:
                continue
            if not card.isUnit:
                continue
            extra = max(hand[card] - 1, 0)
            if card == GRADE_1 and hand[BRANWEN] > 0:
                extra += 1
            for _ in range(extra):
                hand[card] -= 1
                cardsToReturn.append(card)
    DebugPrint(f"Putting {cardsToReturn} to bottom")
    redraw = random.sample(deck, len(cardsToReturn))
    for card in redraw:
        hand[card] += 1
        deck.remove(card)
    DebugPrint(f"Post mulligan: {hand}")
    deck += cardsToReturn
    foundGrades = [0, 0, 0]
    for card in hand:
        if hand[card] > 0 and card.grade > 0 and card.isUnit:
            index = card.grade - 1
            foundGrades[index] = 1
    if np.sum(foundGrades) == 3:
        for card in hand:
            hand[card] = 0
        return 1
    
    lastTurn = 3
    usedGAssist = False
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choice(deck)
        deck.remove(draw)
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
            topFive = random.sample(deck, 5)
            for card in topFive:
                if card.grade != next_grade:
                    continue
                if not card.isUnit:
                    continue
                deck.remove(card)
                rideTarget.append(card)
                break
        if rideTarget:
            vanguard = rideTarget.pop()
            DebugPrint(f"Rode {vanguard}")
            if vanguard.grade == 1:
                starter_draw = random.choice(deck)
                deck.remove(starter_draw)
                DebugPrint(f"Drew {starter_draw} off of starter")
                hand[starter_draw] += 1
            if vanguard.grade == 3:
                for card in hand:
                    hand[card] = 0
                return 1
            if vanguard == BRANWEN:
                topFive = random.sample(deck, 5)
                if GRADE_3 in topFive:
                    deck.remove(GRADE_3)
                    hand[GRADE_3] += 1
        else:
            DebugPrint("Missed ride")

        # Main phase
        while hand[BRANWEN] > 0:
            DebugPrint("Called Branwen")
            hand[BRANWEN] -= 1
            topFive = random.sample(deck, 5)
            if GRADE_3 in topFive:
                deck.remove(GRADE_3)
                hand[GRADE_3] += 1

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = random.choice(deck)
            deck.remove(driveCheck)
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1

    for card in hand:
        hand[card] = 0
    return 0

def Mean(data: list):
    p = np.mean(data)
    return p

premium = GameEnvironment([TRIGGER, BRANWEN, GRADE_1, GRADE_2, GRADE_3, ORDER, STARTER], 
                          50, RunGame, Mean)