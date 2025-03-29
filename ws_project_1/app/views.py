from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils.sparql_client import query_player_details, query_club_details, query_club_players, query_all_players, query_all_clubs, query_graph_data

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

    players_data = query_all_players() 

    # Filtering
    search_name = request.GET.get("name", "").strip().lower()
    position = request.GET.get("position", "").strip().lower()
    nation = request.GET.get("nation", "").strip().lower()

    if search_name:
        players_data = [p for p in players_data if search_name in p["name"].lower()]
    if position:
        players_data = [p for p in players_data if position in [pos.lower() for pos in p["positions"]]]
    if nation:
        players_data = [p for p in players_data if nation in p["nation"].lower()]

    for player in players_data:
            player["positions"] = ", ".join(player["positions"])

    # Pagination
    paginator = Paginator(players_data, 15)
    page = request.GET.get("page", 1)

    try:
        players_page = paginator.page(page)
    except PageNotAnInteger:
        players_page = paginator.page(1)
    except EmptyPage:
        players_page = paginator.page(paginator.num_pages)

    return render(request, "players.html", {
        "entities_list": players_page,
        "search_name": search_name,
        "position": position,
        "nation": nation
    })

def clubs(request):

    clubs_data = query_all_clubs()

    search_name = request.GET.get("name", "").strip().lower()
    league = request.GET.get("league", "").strip().lower()

    if search_name:
        clubs_data = [c for c in clubs_data if search_name in c["name"].lower()]
    if league:
        clubs_data = [c for c in clubs_data if league in c["league"].lower()]

    # Pagination
    paginator = Paginator(clubs_data, 15)
    page = request.GET.get("page", 1)

    try:
        clubs_page = paginator.page(page)
    except PageNotAnInteger:
        clubs_page = paginator.page(1)
    except EmptyPage:
        clubs_page = paginator.page(paginator.num_pages)

    return render(request, "clubs.html", {
        "entities_list": clubs_page,
        "search_name": search_name,
        "league": league
    })

def graph_view(request):
    # Get graph data (nodes and relationships) from the SPARQL endpoint
    graph_data = query_graph_data()
    
    # Log the graph data for debugging
    print("Graph data fetched:", len(graph_data["nodes"]) if graph_data.get("nodes") else 0, "nodes")
    
    return render(request, "graph.html", {"graph_data": graph_data})
