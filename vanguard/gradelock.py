import random as random
import numpy as np
from gametools import GameEnvironment, VanguardCard

STARTER = VanguardCard("V Starter", 0, max = 0)
GRADE_1 = VanguardCard("Grade 1", 1)
BRANWEN = VanguardCard("Branwen", 1, min = 4, max = 4)
GRADE_2 = VanguardCard("Grade 2", 2)
GRADE_3 = VanguardCard("Grade 3", 3)

TRIGGER = VanguardCard("Trigger Unit", 0, trigger = True, min = 15, max = 15)
OVER = VanguardCard("Over Trigger", 0, trigger = True, min = 1, max = 1)

# Put cards in order of ride priority
cards = [STARTER, TRIGGER, OVER, BRANWEN, GRADE_1, GRADE_2, GRADE_3]

def RunGame(main_deck: dict, goingSecond: bool, cache = {}, debug = False):
    def DebugPrint(text: str):
        if debug:
            print(text)

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
    for grade in [1,2,3]:
        for card in hand:
            if card.grade != grade:
                continue
            if card in premulligan:
                hand[card] += 1
                premulligan.remove(card)
                break

    for i, _ in enumerate(premulligan):
        hand[postmulligan[i]] += 1
    if (hand[GRADE_1] + hand[BRANWEN] > 0) and (hand[GRADE_2] > 0) and (hand[GRADE_3] > 0):
        return 1
    for card in hand:
        main_deck[card] -= hand[card]
    DebugPrint("Post mulligan: " + str({card: hand[card] for card in hand if hand[card] > 0}))
    
    lastTurn = 3
    opponents_grade = 1 if goingSecond else 0
    for turn in range(lastTurn):
        DebugPrint(f"---------------- Turn {turn+1} --------------------")
        draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[draw] -= 1
        hand[draw] += 1
        DebugPrint(f"Drew {draw}")

        # Ride step
        ride_target = []
        for card in hand:
            if hand[card] == 0:
                continue
            if card.grade == vanguard.grade + 1:
                hand[card] -= 1
                ride_target = [card]
        if ride_target:
            vanguard = ride_target[0]
            DebugPrint(f"Rode {vanguard}")
            if vanguard.grade == 1:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1
                DebugPrint(f"Drew {draw} off of starter")
            if vanguard == BRANWEN:
                search_range = random.sample(cards, k = 5, counts=list(main_deck.values()))
                if GRADE_3 in search_range:
                    hand[GRADE_3] += 1
                    main_deck[GRADE_3] -= 1
                    DebugPrint(f"Added grade 3 from Branwen clone")
        if vanguard.grade == 3:
            return 1
        DebugPrint("Hand: " + str({card: hand[card] for card in hand if hand[card] > 0}))

        # Main phase
        while hand[BRANWEN] > 0:
            hand[BRANWEN] -= 1
            DebugPrint(f"Called Branwen clone")
            search_range = random.sample(cards, k = 5, counts=list(main_deck.values()))
            if GRADE_3 in search_range:
                hand[GRADE_3] += 1
                main_deck[GRADE_3] -= 1
                DebugPrint(f"Added grade 3 from Branwen clone")

        # Battle phase
        drives = 1 if vanguard.grade < 3 else 2
        if opponents_grade == 0:
            drives = 0
        for _ in range(drives):
            check = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[check] -= 1
            if check != OVER:
                hand[check] += 1
            DebugPrint(f"Drove check {check}")
            if check == OVER:
                draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
                main_deck[draw] -= 1
                hand[draw] += 1

        # Opponent's turn
        opponents_grade += 1
        damage = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
        main_deck[damage] -= 1
        DebugPrint(f"Damage checked {damage}")
        if damage == OVER:
            draw = random.choices(cards, weights=list(main_deck.values()), k=1)[0]
            main_deck[draw] -= 1
            hand[draw] += 1

    return 0

def Mean(data: list):
    mu = np.mean(data)
    return mu

test = GameEnvironment(cards, 49, RunGame, Mean)