import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Ride Deck G0", 0, inRideDeck=True, max = 0)
RIDE_G1 = VanguardCard("Ride Deck G1", 1, inRideDeck=True, max = 0)
RIDE_G2 = VanguardCard("Ride Deck G2", 2, inRideDeck=True, max = 0)
RIDE_G3 = VanguardCard("Ride Deck G3", 3, inRideDeck=True, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 13, max = 13)
FRONT = VanguardCard("Soul Front", 0, trigger = True, min = 3, max = 3)

SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

NORMAL = VanguardCard("Normal Unit", 2)
YUIKA = VanguardCard("Yuika", 1, min = 4, max = 4)
VALEFR = VanguardCard("Valefr", 0, min = 0, max = 4)
RAINBOW = VanguardCard("Seven Hues Bridge, Lucciel", 2, min = 4, max = 4)

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
    for keep in [SENTINEL, PERSONA, RAINBOW, YUIKA]:
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
    
    lastTurn = 5
    field = []
    soul = 0
    soul_needed = 0
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = main_deck.pop()
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        if ride_deck:
            vanguard = ride_deck.pop()
            soul += 1
            DebugPrint(f"Rode {vanguard}")
            if vanguard.grade == 1 and goingSecond:
                hand[main_deck.pop()] += 1
        elif hand[PERSONA] > 0:
            soul += 1
            hand[PERSONA] -= 1
            hand[main_deck.pop()] += 1
        DebugPrint(hand)

        # Main phase
        while vanguard.grade >= 2 and hand[RAINBOW] > 0:
            hand[RAINBOW] -= 1
            field.append(RAINBOW)
            soul_needed += 1
        if vanguard.grade >= 2 and hand[YUIKA] > 0 and field.count(YUIKA) < 2:
            hand[YUIKA] -= 1
            field.append(YUIKA)

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if not goingSecond and turn == 0:
            drives = 0
        for _ in range(drives):
            driveCheck = main_deck.pop()
            DebugPrint(f"Drove check {driveCheck}")
            hand[driveCheck] += 1
        for card in field:
            if card != YUIKA:
                continue
            soul_needed += 1
            if RAINBOW in field:
                field.remove(RAINBOW)
                hand[RAINBOW] += 1

        if turn + 1 < lastTurn and hand[FRONT] > 0:
            hand[FRONT] -= 1
            soul += 1

    return soul - soul_needed

def Mean(data: list):
    p = np.mean(data)
    return -abs(p)

artisaria = GameEnvironment([STARTER, RIDE_G1, RIDE_G2, RIDE_G3, SENTINEL, PERSONA, NORMAL, YUIKA, RAINBOW, FRONT, TRIGGER], 
                          50, RunGame, Mean)