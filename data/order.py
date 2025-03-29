# Read players.csv and order them by 'Rk' column

import pandas as pd
import os
import csv

df = pd.read_csv('players.csv')

# Print how many players are in the file
print(f"Number of players in the file: {len(df)}")

# Find what players are missing from the file
# If, for example, [1,2,3,4,5] are missing, group them and print them as [1-5]
# The total number of players is 2752
total_players = 2752
missing_players = []
for i in range(1, total_players + 1):
    if i not in df['Rk'].values:
        missing_players.append(i)

if missing_players:
    grouped_missing = []
    start = missing_players[0]
    end = missing_players[0]

    for i in range(1, len(missing_players)):
        if missing_players[i] == end + 1:
            end = missing_players[i]
        else:
            if start == end:
                grouped_missing.append(f"{start}")
            else:
                grouped_missing.append(f"{start}-{end}")
            start = missing_players[i]
            end = missing_players[i]

    if start == end:
        grouped_missing.append(f"{start}")
    else:
        grouped_missing.append(f"{start}-{end}")

    print(f"Missing players: {', '.join(grouped_missing)}")

df = df.sort_values(by='Rk')
df.to_csv('players.csv', index=False)