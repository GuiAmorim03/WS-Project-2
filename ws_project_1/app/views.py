from django.shortcuts import render
from .utils.sparql_client import query_player_details

def player_detail(request, player_id):
    # Get player data from the SPARQL endpoint
    player_data = query_player_details(player_id)
    # Log the player data
    print(player_data)
    return render(request, "player.html", {"entity": player_data})

def team_detail(request, team_id):
    team_data = {
        "name": "Paris Saint-Germain",
        "stadium": "Parc des Princes",
        "city": "Paris",
        "league_id": 'fr',
        "league_name": "Ligue 1",
        "league_flag": "https://a.espncdn.com/i/teamlogos/countries/500/fra.png",
        "color": "0C2C56",
        "alternate_color": "FFFFFF",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/160.png",

        "players": [
            {
                "id": "aaron_malouda",
                "name": "Aaron Malouda",
                "age": 2025 - 2005,
                "pos": ["DF", "MD"],
                "country_name": "France",
                "country_flag": "https://a.espncdn.com/i/teamlogos/countries/500/fra.png",
            },
            {
                "id": "benoit_lafont",
                "name": "Benoit Lafont",
                "age": 2025 - 1998,
                "pos": ["GK"],
                "country_name": "Portugal",
                "country_flag": "https://a.espncdn.com/i/teamlogos/countries/500/por.png",
            }
        ],
    }

    return render(request, "team.html", {"entity": team_data})