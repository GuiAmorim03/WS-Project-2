import pandas as pd
import random
import csv
import time

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.error import HTTPError

def get_player_photo_url_by_profile_page(url):
    """
    Given a player profile page URL of zerozero.pt, return the URL of the player's photo.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]

    headers = {'User-Agent': random.choice(user_agents)}
    req = Request(url, headers=headers)
    response = urlopen(req).read()

    soup = BeautifulSoup(response, 'html.parser')

    div_image = soup.find('div', class_='profile_picture')
    div_logo = div_image.find('div', class_='logo')
    a = div_logo.find('a')
    img = a.find('img')
    img_url = img['src']
    
    return img_url


def parserLeagueEN(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]

    headers = {'User-Agent': random.choice(user_agents)}
    req = Request(url, headers=headers)
    response = urlopen(req).read()

    soup = BeautifulSoup(response, 'html.parser')

    div_player = soup.find('div', class_='playerContainer')
    img_player = div_player.find('div', class_='imgContainer').find('img')['data-player']

    return f"https://resources.premierleague.com/premierleague/photos/players/250x250/{img_player}.png"

def parserLeagueDE(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]

    headers = {'User-Agent': random.choice(user_agents)}
    req = Request(url, headers=headers)
    response = urlopen(req).read()

    soup = BeautifulSoup(response, 'html.parser')

    div_player = soup.find('player-image')
    img_player = div_player.find('img')['src']

    return img_player

def parserLeagueIT(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]

    headers = {'User-Agent': random.choice(user_agents)}
    req = Request(url, headers=headers)
    response = urlopen(req).read()

    soup = BeautifulSoup(response, 'html.parser')

    img_player = soup.find('img', class_='hm-img-player')["src"]

    return img_player

def parserLeagueFR(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]

    headers = {'User-Agent': random.choice(user_agents)}
    req = Request(url, headers=headers)
    response = urlopen(req).read()

    soup = BeautifulSoup(response, 'html.parser')

    div_player = soup.find('div', class_='right_10 pos_relative items_center')
    img_player = div_player.find('img')['src']

    return img_player

df_main = pd.read_csv('players_data_light-2024_2025.csv')

output_file = "players.csv"

# print(get_player_photo_url_by_profile_page("https://www.zerozero.pt/jogador/mohamed-abdelmonem/817977"))
# print(parserLeagueEN("https://www.premierleague.com/players/72371/Jo%C3%A3o-Pedro/overview"))
# print(parserLeagueDE("https://www.bundesliga.com/en/bundesliga/player/philipp-lienhart"))
# print(parserLeagueFR("https://ligue1.fr/player-sheet/l1_championship_player_2024_13_93848?tab=profile"))
# print(parserLeagueIT("https://www.legaseriea.it/it/player/tammy-abraham-90074"))


with open(output_file, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    writer.writerow(["Rk", "Player", "UrlWebsite", "UrlPhoto"])

    for index, row in df_main.iterrows():
        rk = row['Rk']
        if rk < 2735:
            continue
        name = row['Player']
        club = row['Squad']
        league = row['Comp']

        league_code = league.split(" ")[0]
        if league_code == "eng" or league_code == "de":
            if league_code == "eng":
                website = "premierleague.com"
                parser = parserLeagueEN
            elif league_code == "it":
                website = "legaseriea.it"
            elif league_code == "de":
                website = "bundesliga.com"
                parser = parserLeagueDE
            elif league_code == "fr":
                website = "ligue1.fr"

            to_search = f"{website} {name}"
            try:
                player_url = next(search(to_search, num_results=1))
                img_url = parser(player_url)
            except Exception as e:
                print(f"Error: {e}")
                if "429 Client Error" in str(e):
                    print("Erro 429: Muitas requisições! Encerrando programa.")
                    exit(1)
                else:                
                    player_url = None
                    img_url = None
            time.sleep(random.randint(5, 10))


        else:
            player_url = None
            img_url = None

        # to_search = f"{name} {club} zerozero"
        # zerozero_url = next(search(to_search, num_results=1))
        # if "zerozero.pt" in zerozero_url:
        #     photo_url = get_player_photo_url_by_profile_page(zerozero_url)
        # else:
        #     photo_url = None
        writer.writerow([rk, name, player_url, img_url])
        file.flush()

