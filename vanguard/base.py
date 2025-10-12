import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("Ride Deck G0", 0, max = 0)
RIDE_G1 = VanguardCard("Ride Deck G1", 1, max = 0)
RIDE_G2 = VanguardCard("Ride Deck G2", 2, max = 0)
RIDE_G3 = VanguardCard("Ride Deck G3", 3, max = 0)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)
SENTINEL = VanguardCard("Perfect Guard", 1, min = 4, max = 4)
PERSONA = VanguardCard("Persona Ride", 3, min = 3, max = 3)

NORMAL = VanguardCard("Normal Unit", 2)

cards = [NORMAL, TRIGGER, OVER, SENTINEL, PERSONA, 
         STARTER, RIDE_G1, RIDE_G2, RIDE_G3]

def RunGame(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)

    ride_deck = [RIDE_G3, RIDE_G2, RIDE_G1]
    vanguard = STARTER
    
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
        if card == SENTINEL and hand[SENTINEL] > 0:
            continue
        if card == PERSONA and hand[PERSONA] > 0:
            continue
        premulligan.remove(card)
        hand[card] += 1

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1

    for card in hand:
        main_deck[card] -= hand[card]
    DebugPrint("Post mulligan: " + str({card: hand[card] for card in hand if hand[card] > 0}))
    
    lastTurn = 3
    energy = 0 if goingSecond else -3
    opponents_grade = 1 if goingSecond else 0
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[draw] -= 1
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")
        # Ride step
        energy += 3
        if ride_deck:
            vanguard = ride_deck.pop()
            DebugPrint(f"Rode {vanguard}")
            if vanguard.grade == 1 and goingSecond:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Drew {draw} off of starter")
        elif hand[PERSONA] > 0:
            hand[PERSONA] -= 1
            draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[draw] -= 1
            hand[draw] += 1
            DebugPrint(f"Persona ride! Drew {draw}")
        DebugPrint(hand)

        # Main phase

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            check = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[check] -= 1
            hand[check] += 1
            DebugPrint(f"Drove check {check}")

        # Opponent's turn
        opponents_grade += 1
        damage = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[damage] -= 1
        DebugPrint(f"Damage checked {damage}")

    return 1

def Mean(data: list):
    mu = np.mean(data)
    return mu

template_sim = GameEnvironment(cards, 50, RunGame, Mean)