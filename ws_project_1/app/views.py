from django.shortcuts import render
from .utils.sparql_client import query_player_details, query_club_details, query_club_players

def player_detail(request, player_id):
    # Get player data from the SPARQL endpoint
    player_data = query_player_details(player_id)
    # Log the player data
    print(player_data)
    return render(request, "player.html", {"entity": player_data})

def club_detail(request, club_id):
    # Get club data from the SPARQL endpoint
    club_data = query_club_details(club_id)
    
    # Get players data from the SPARQL endpoint
    players = query_club_players(club_id)
    
    # Format players data to match template expectations
    formatted_players = []
    for player in players:
        formatted_players.append({
            "id": player["id"],
            "name": player["name"],
            "age": player["age"],
            "pos": player["positions"],  # Note the field name change from positions to pos
            "country_name": player["nation"],
            "country_flag": player["flag"]
        })
    
    # Add players to club data
    club_data["players"] = formatted_players
    
    # Log the club data
    print(club_data)
    
    return render(request, "club.html", {"entity": club_data})

def dashboard(request):
    return render(request, "dashboard.html", {"stats": {}})

def players(request):
    return render(request, "players.html", {"entities_list": []})

def clubs(request):
    return render(request, "clubs.html", {"entities_list": []})