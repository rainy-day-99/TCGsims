import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("D Starter", 0, inRideDeck=True, min = 1, max = 1)
RIDE_G1 = VanguardCard("Ride Deck G1", 1, inRideDeck=True, min = 1, max = 1)
RIDE_G2 = VanguardCard("Ride Deck G2", 2, inRideDeck=True, min = 1, max = 1)
RIDE_G3 = VanguardCard("Ride Deck G3", 3, inRideDeck=True, min = 1, max = 1)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
OBSCUDEID = VanguardCard("Obscudeid", 3, min = 5, max = 5)

NORMAL = VanguardCard("Normal Unit", 2)
ORDER = VanguardCard("Research Order", 1, unit = False, min = 0, max = 8)

def RunGame(main_deck: list[VanguardCard], hand: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)

    ride_deck = []
    for _ in range(4):
        ride_deck.append(main_deck.pop(0))
    if len(ride_deck) != 4:
        print("Ride deck not full!")
        return(0)
    ride_deck.sort(key = lambda x: x.grade, reverse=True)
    vanguard = ride_deck.pop()

    random.shuffle(main_deck)
    startingHandSize = 5
    premulligan = {card: 0 for card in hand}
    for _ in range(startingHandSize):
        premulligan[main_deck.pop()] += 1
    DebugPrint(f"Premulligan: {premulligan}")
    
    # Mulligan step
    keeping: int = premulligan[NORMAL]
    hand[NORMAL] += keeping
    premulligan[NORMAL] -= keeping
    
    if premulligan[SENTINEL] > 0:
        premulligan[SENTINEL] -= 1
        hand[SENTINEL] += 1

    if premulligan[ORDER] > 0:
        premulligan[ORDER] -= 1
        hand[ORDER] += 1
    
    cardsPutBack = []
    for card in premulligan:
        cardsPutBack += [card] * premulligan[card]
    DebugPrint(f"Putting back {cardsPutBack}")
    for _ in cardsPutBack:
        hand[main_deck.pop()] += 1
    main_deck += cardsPutBack
    random.shuffle(main_deck)
    DebugPrint(f"Post mulligan: {hand}")
    
    orders = 0
    lastTurn = 3
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = main_deck.pop()
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        if ride_deck:
            vanguard = ride_deck.pop()
            if vanguard.grade != 3 and ORDER in main_deck:
                hand[ORDER] += 1
                main_deck.remove(ORDER)
                random.shuffle(main_deck)
            if vanguard.grade == 1 and goingSecond:
                hand[main_deck.pop()] += 1
        DebugPrint(hand)

        # Main phase
        if hand[ORDER] > 0:
            hand[ORDER] -= 1
            orders += 1
            DebugPrint("Played an order.")
        DebugPrint(f"Order count: {orders}")
        if vanguard.grade == 3:
            break

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = main_deck.pop()
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1

    if orders == 3 and hand[ORDER] <= 1:
        return 1
    return 0

def Mean(data: list):
    p = np.mean(data)
    return p

eva = GameEnvironment([STARTER, RIDE_G1, RIDE_G2, RIDE_G3, SENTINEL, OBSCUDEID, NORMAL, ORDER, TRIGGER], 
                          54, RunGame, Mean)