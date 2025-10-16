from vanguard.Lianorn.rosarium import lianorn as game
import numpy as np

all_decks = [[i] for i in range(game.cards[0].min, game.cards[0].max + 1) if i<= game.maxDeckSize]
for card in game.cards[1:]:
    new_decks = []
    for deck in all_decks:
        for i in range(card.min, card.max + 1):
            new_deck = deck + [i]
            new_decks.append(new_deck)
    all_decks = new_decks

deck_ids = []
for deck in all_decks:
    id = tuple(deck)
    if game.CheckIfValid(id):
        deck_ids.append(id)
deck_ids.sort()
results = {deck: [] for deck in deck_ids}

game_length = 200000
best_deck = None
best_result = 0
for deck in results:
    game_results = np.array(game.PlayGames(deck, game_length))
    mu = game.ReturnScore(game_results)
    if best_result < mu:
        best_deck = deck
    results[deck] = game_results


print("\n##### Final Results #####\n")
for deck in results:
    color = "\033[38;5;220m" if deck == best_deck else "\033[38;5;255m"
    print(color,[f"{game.cards[i]}: {count}" for i, count in enumerate(deck) if game.cards[i].min != game.cards[i].max])
    print(color,f" - Mean: {np.mean(results[deck]):.3f}\t\t - Score: {game.ReturnScore(results[deck])}")

