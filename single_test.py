from vanguard.Lianorn.unisonDress import lianorn as game

games_to_play = 10000

default_deck = game.CreateInitialDeck()
debug_sim = (games_to_play == 1)

output = game.PlayGames(default_deck, games_to_play, debug_sim)
for i in set(output):
    print(f"{i}:\t {output.count(i)}")
game.ReturnScore(output)