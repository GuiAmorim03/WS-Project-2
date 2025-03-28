import pandas as pd
import random
import csv
import time

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from googlesearch import search

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


df_main = pd.read_csv('players_data_light-2024_2025.csv')

output_file = "players.csv"

with open(output_file, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # writer.writerow(["Rk", "Player", "UrlWebsite", "UrlPhoto"])

    for index, row in df_main.iterrows():
        rk = row['Rk']
        # if rk < 63:
        #     continue
        name = row['Player']
        club = row['Squad']

        to_search = f"{name} {club} zerozero"
        zerozero_url = next(search(to_search, num_results=1))
        if "zerozero.pt" in zerozero_url:
            photo_url = get_player_photo_url_by_profile_page(zerozero_url)
        else:
            photo_url = None
        writer.writerow([rk, name, zerozero_url, photo_url])
        file.flush()

        time.sleep(5)