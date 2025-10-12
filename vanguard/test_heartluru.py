import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Toy G0", 0, inRideDeck=True, max = 0)
RIDE_G1 = VanguardCard("Toy G1", 1, inRideDeck=True, max = 0)
RIDE_G2 = VanguardCard("Toy G2", 2, inRideDeck=True, max = 0)
RIDE_G3 = VanguardCard("Heartluru", 3, inRideDeck=True, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 16, max = 16)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Heartluru", 3, min = 3, max = 3)

SET_ORDER = VanguardCard("Toys Are Made For Children", 1, unit = False, min = 4, max = 4)
HAPPY_TOYS = VanguardCard("Generic Happy Toys", 2, max = 19)
PHILYA = VanguardCard("Philya", 1)
WRESTER = VanguardCard("Avarice Wrester", 1, max = 4)
NORMAL = VanguardCard("Normal Unit", 2)

cards = [NORMAL, TRIGGER, SENTINEL, PERSONA, 
         SET_ORDER, HAPPY_TOYS, WRESTER, PHILYA,
         STARTER, RIDE_G1, RIDE_G2, RIDE_G3]

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

    startingHandSize = 5
    mulligan_range = random.sample(main_deck, k = startingHandSize * 2)
    premulligan = mulligan_range[:startingHandSize]
    redraw = mulligan_range[startingHandSize:]
    DebugPrint(f"Premulligan: {premulligan}")
    
    # Mulligan step
    for keep in [SENTINEL, PERSONA, SET_ORDER, WRESTER, PHILYA]:
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
    
    lastTurn = 4
    orders = 0
    soul = []
    drop = []
    advantage_gained = 0
    energy = 0 if goingSecond else -3
    opponents_grade = 1 if goingSecond else 0
    nutcracker_search = False
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choice(main_deck)
        hand[draw] += 1
        main_deck.remove(draw)
        DebugPrint(f"Drew {draw}")

        # Ride step
        energy += 3
        if ride_deck:
            if hand[HAPPY_TOYS]:
                hand[HAPPY_TOYS] -= 1
                drop.append(HAPPY_TOYS)
            soul.append(vanguard)
            vanguard = ride_deck.pop()
            DebugPrint(f"Rode {vanguard}")
            if (vanguard.grade < 3) and (SET_ORDER in main_deck):
                main_deck.remove(SET_ORDER)
                hand[SET_ORDER] += 1
            if vanguard.grade == 1 and goingSecond:
                draw = random.choice(main_deck)
                hand[draw] += 1
                main_deck.remove(draw)
        elif hand[PERSONA] > 0:
            soul.append(RIDE_G3)
            vanguard = PERSONA
            hand[PERSONA] -= 1
            draw = random.choice(main_deck)
            hand[draw] += 1
            main_deck.remove(draw)
        DebugPrint(hand)

        # Main phase
        if hand[SET_ORDER] == 0 and (SET_ORDER in main_deck):
            if (nutcracker_search) and (STARTER in soul):
                soul.remove(STARTER)
                main_deck.remove(SET_ORDER)
                hand[SET_ORDER] += 1
                advantage_gained -= 1
            elif hand[WRESTER] > 0:
                hand[WRESTER] -= 1
                advantage_gained -= 1
                main_deck.remove(SET_ORDER)
                hand[SET_ORDER] += 1

        if hand[SET_ORDER]:
            hand[SET_ORDER] -= 1
            orders += 1
            toy_search = random.sample(main_deck, k = 5)
            if HAPPY_TOYS in toy_search:
                toy_search.remove(HAPPY_TOYS)
                hand[HAPPY_TOYS] += 1
                main_deck.remove(HAPPY_TOYS)
            if HAPPY_TOYS in toy_search:
                soul.append(HAPPY_TOYS)
                main_deck.remove(HAPPY_TOYS)
        for _ in range(orders // 2):
            if HAPPY_TOYS in drop:
                drop.remove(HAPPY_TOYS)
                soul.append(HAPPY_TOYS)

        card: VanguardCard
        for _ in range(orders):
            if vanguard.grade < 3:
                break
            if RIDE_G1 in soul:
                soul.remove(RIDE_G1)
                advantage_gained += 1
                nutcracker_search = True
            elif HAPPY_TOYS in soul:
                soul.remove(HAPPY_TOYS)
                advantage_gained += 1
            elif RIDE_G2 in soul:
                soul.remove(RIDE_G2)
                advantage_gained += 1

        # Battle phase
        for _ in range(orders // 2):
            advantage_gained += 1 if vanguard.grade == 3 else 0
            
        drives = 1 if vanguard.grade < 3 else 2
        if orders == 3 and opponents_grade >= 3:
            drives = 3
        if opponents_grade == 0:
            drives = 0
        if drives > 0:
            draws = random.sample(main_deck, k = hand[PHILYA])
            hand[PHILYA] = 0
            for card in draws:
                main_deck.remove(card)
                hand[card] += 1
        driveChecks = random.sample(main_deck, k = drives)
        for check in driveChecks:
            DebugPrint(f"Drove check {check}")
            hand[check] += 1
            main_deck.remove(check)

        opponents_grade += 1

    return advantage_gained

def Distance(data: list):
    # return max(data)
    mu = np.mean(data)
    # return mu
    # The theoretical maximum for the number of Mythischs called is 10, so our target is 1 less than that.
    target = 11
    return -(mu - target) ** 2

def Mean(data: list):
    return np.mean(data)

def Limit(data: list):
    # Call 3 units on turn 3
    # Restand once on turn 3
    # Call 4 units on turn 4
    # Restand twice on turn 4
    n = len(data)
    best = data.count(max(data)) / n
    next_best = data.count(max(data)-1) / n
    score = 10 ** (next_best - best)
    if best < next_best:
        return (score - 1)
    else:
        return score

heartluru = GameEnvironment(cards, 50, RunGame, Limit)

# 8.7822, unlimited orders and Happy Toys, keep one in hand
# 8.8041, unlimited orders and Happy Toys, keep two in hand

# y = 1 - x
# When x10 = x9, y1 = 0
# y = m(0-x1)
