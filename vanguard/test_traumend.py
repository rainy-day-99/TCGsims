import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Corphie", 0, inRideDeck=True, max = 0)
RIDE_G1 = VanguardCard("Gracia", 1, inRideDeck=True, max = 0)
RIDE_G2 = VanguardCard("Rektina", 2, inRideDeck=True, max = 0)
RIDE_G3 = VanguardCard("Lianorn Traumend", 3, inRideDeck=True, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
SINCERIETE = VanguardCard("Sinceriete", 1, min = 4, max = 4)
LIANORN = VanguardCard("Lianorn Vivace/Traumend", 3, max = 7)
NORMAL = VanguardCard("Normal Unit", 2)

cards = [NORMAL, TRIGGER, SENTINEL, LIANORN, SINCERIETE,
         STARTER, RIDE_G1, RIDE_G2, RIDE_G3]

def RunGame(main_deck: list[VanguardCard], hand: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)

    ride_deck = [RIDE_G3, RIDE_G2, RIDE_G1]
    vanguard = STARTER

    startingHandSize = 5
    mulligan_range = random.sample(main_deck, k = startingHandSize * 2)
    premulligan = mulligan_range[:startingHandSize]
    redraw = mulligan_range[startingHandSize:]
    DebugPrint(f"Premulligan: {premulligan}")
    
    # Mulligan step
    while SINCERIETE in premulligan:
        premulligan.remove(SINCERIETE)
        hand[SINCERIETE] += 1
    for keep in [SENTINEL, LIANORN, SINCERIETE]:
        if keep in premulligan:
            premulligan.remove(keep)
            hand[keep] += 1

    DebugPrint(f"Putting back {premulligan}")
    for _ in premulligan:
        hand[redraw.pop()] += 1
    for card in hand:
        for _ in range(hand[card]):
            main_deck.remove(card)
    DebugPrint(f"Post mulligan: {hand}")
    
    # goingSecond = True
    lastTurn = 3
    energy = 0 if goingSecond else -3
    opponents_grade = 1 if goingSecond else 0
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choice(main_deck)
        hand[draw] += 1
        main_deck.remove(draw)
        DebugPrint(f"Drew {draw}")

        # Ride step
        energy += 3
        if ride_deck:
            vanguard = ride_deck.pop()
            DebugPrint(f"Rode {vanguard}")
            if hand[SINCERIETE] > 0:
                hand[SINCERIETE] -= 1
                draw = random.choice(main_deck)
                hand[draw] += 1
                main_deck.remove(draw)
            if vanguard.grade == 1 and goingSecond:
                draw = random.choice(main_deck)
                hand[draw] += 1
                main_deck.remove(draw)
        DebugPrint(hand)

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 3
        if opponents_grade == 0:
            drives = 0
        driveChecks = random.sample(main_deck, k = drives)
        for check in driveChecks:
            DebugPrint(f"Drove check {check}")
            hand[check] += 1
            main_deck.remove(check)
        if hand[LIANORN] > 1 and opponents_grade >= 3:
            hand[LIANORN] -= 1
            extraDrive = random.choice(main_deck)
            main_deck.remove(extraDrive)
            hand[extraDrive] += 1

        opponents_grade += 1

    while hand[SENTINEL] > 0 and hand[LIANORN] > 1:
        hand[LIANORN] -= 1
        hand[SENTINEL] -= 1
    return hand[LIANORN]

def Distance(data: list):
    mu = np.mean(data)
    # Ideally we would like a Lianorn (either Vivace or Traumend)
    # Having more than one at the end of turn is a waste, so we aim for exactly 1
    target = 1
    return -(mu - target) ** 2

def Mean(data: list):
    return np.mean(data)

traumend = GameEnvironment(cards, 50, RunGame, Distance)
