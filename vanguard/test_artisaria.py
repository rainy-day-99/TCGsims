import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Ride Deck G0", 0, inRideDeck=True, max = 0)
RIDE_G1 = VanguardCard("Ride Deck G1", 1, inRideDeck=True, max = 0)
RIDE_G2 = VanguardCard("Ride Deck G2", 2, inRideDeck=True, max = 0)
RIDE_G3 = VanguardCard("Ride Deck G3", 3, inRideDeck=True, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

NORMAL = VanguardCard("Normal Unit", 2)
ORDER = VanguardCard("Sound System", 3, unit = False, min = 0, max = 8)

def RunGame(main_deck: list[VanguardCard], hand: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)

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
    for keep in [SENTINEL, PERSONA, ORDER]:
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
    
    orders = 0
    lastTurn = 5
    drop = []
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = main_deck.pop()
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        if ride_deck:
            vanguard = ride_deck.pop()
            DebugPrint(f"Rode {vanguard}")
            if hand[ORDER] > 0:
                hand[ORDER] -= 1
                drop.append(ORDER)
            if vanguard.grade != 3 and ORDER in main_deck:
                hand[ORDER] += 1
                main_deck.remove(ORDER)
                random.shuffle(main_deck)
            if vanguard.grade == 1 and goingSecond:
                hand[main_deck.pop()] += 1
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            hand[main_deck.pop()] += 1
        DebugPrint(hand)

        # Main phase
        if vanguard.grade == 3:
            if hand[ORDER] > 0:
                hand[ORDER] -= 1
                orders += 1
                hand[main_deck.pop()] += 1
                DebugPrint("Played an order from hand.")
            elif drop:
                orders += 1
                drop.pop()
                DebugPrint("Played an order from drop.")
        DebugPrint(f"Order count: {orders}")

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = main_deck.pop()
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1

    if orders < 3:
        return 0
    if hand[ORDER] > 1:
        return 0
    return 1

def Mean(data: list):
    p = np.mean(data)
    return p

artisaria = GameEnvironment([STARTER, RIDE_G1, RIDE_G2, RIDE_G3, SENTINEL, PERSONA, NORMAL, ORDER, TRIGGER], 
                          50, RunGame, Mean)