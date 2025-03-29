import pandas as pd

df_main = pd.read_csv("players_leagues.csv")
df_zerozero = pd.read_csv("players_zerozero.csv")

for index, row in df_main.iterrows():

    if pd.isna(row['UrlPhoto']):
        # procurar pela linha no zerozero com mesmo Rk
        try:
            row_zerozero = df_zerozero[df_zerozero['Rk'] == row['Rk']]
            if len(row_zerozero) > 0:
                # se encontrar, copiar a url da foto
                df_main.at[index, 'UrlWebsite'] = row_zerozero.iloc[0]['UrlWebsite']
                df_main.at[index, 'UrlPhoto'] = row_zerozero.iloc[0]['UrlPhoto']
        except Exception as e:
            print(f"Error processing row {index}: {e}")
# salvar o dataframe atualizado
df_main.to_csv("players.csv", index=False)