from Tests.template import game
import numpy as np
import pandas as pd
from time import time
from datetime import timedelta
from Algorithms.montecarlo import local_search
from Algorithms.bruteforce import broad_search
from os import get_terminal_size


def single_test(game = game, num_sims = 200000):
      initial_deck = game.CreateInitialDeck()
      game.RunGames(initial_deck, num_sims)
      return {initial_deck.key: initial_deck}

search_choice = {
      'local-search': local_search, 
      'broad-search': broad_search,
      'single-test': single_test
}

start = time()
decks = search_choice['broad-search'](game, 400000)
duration = str(timedelta(seconds = round(time() - start)))

column_names = game.variables + ['Score', 'n', 'Mean']
table = pd.DataFrame(columns=column_names)
total_games_played = 0
for i, deck in enumerate(decks.values()):
      mu = np.around(np.mean(deck.results, axis=0), 4)
      score = np.around(game.Score(deck, statistic='mean'), 4)
      n = deck.games_played
      table.loc[i] = [deck.recipe[card] for card in game.variables] + [score, n, mu]
      total_games_played += deck.games_played

table.sort_values("Score", ascending=False, inplace=True, ignore_index=True)
top10 = table[:10]

print("".center(get_terminal_size()[0], '-'))
print("   Final results   ".center(get_terminal_size()[0], ' '))
print("".center(get_terminal_size()[0], '-'))
print(top10)
print(f"\n{total_games_played} total simulations, finished in {duration}")

mean_as_list = pd.DataFrame(table["Mean"].to_list())
table.drop("Mean", axis=1, inplace=True)
output = table.join(mean_as_list)

# with pd.ExcelWriter("ExcelOutputs/frequency.xlsx", engine="openpyxl", 
#                     mode="a", if_sheet_exists="replace"
#                     ) as w:
#       output.to_excel(w, sheet_name="3 turns")