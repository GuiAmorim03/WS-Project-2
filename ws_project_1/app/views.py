from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils.sparql_client import query_player_club, query_player_details, query_club_details, query_club_players, query_all_players, query_all_clubs, query_graph_data, query_top_players_by_stat, query_top_clubs_by_stat, query_all_nations, create_player, update_player_club
from unidecode import unidecode

def player_detail(request, player_id):
    # Get player data from the SPARQL endpoint
    player_data = query_player_details(player_id)
    # Log the player data

    available_clubs = query_all_clubs()

    return render(request, "player.html", {
        "player_id": player_id,
        "entity": player_data, 
        "available_clubs": available_clubs,
    })

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
            "photo_url": player["photo_url"],
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
    """
        matches played  (só players)
        goals
        assists (só players)
        penaltis scored
        passes
        fouls
        saves  (só players)
        cleansheets  (só players)
        yellow cards
        red cards
    """

    stats_to_get = [
        {"id": "mp",  "both_entities": False},
        {"id": "gls", "both_entities": True},
        {"id": "ast", "both_entities": False},
        {"id": "pk", "both_entities": True},
        {"id": "cmp_stats_passing_types", "both_entities": True},
        {"id": "fls", "both_entities": True},
        {"id": "saves", "both_entities": False},
        {"id": "cs",  "both_entities": False},
        {"id": "crdy",  "both_entities": True},
        {"id": "crdr",  "both_entities": True}
    ]

    stats = [
        {
            "entity": "Player",
            "stats": []
        },
        {
            "entity": "Club",
            "stats": []
        }
    ]
    

    for stat_to_get in stats_to_get:
        if stat_to_get["both_entities"]:
            clubs = query_top_clubs_by_stat(stat_to_get["id"])
            stats[1]["stats"].append(clubs)
        players = query_top_players_by_stat(stat_to_get["id"])
        stats[0]["stats"].append(players)

    print(stats)

    return render(request, "dashboard.html", {"stats": stats})

def players(request):

    if request.method == "POST":

        name = request.POST.get("name", "")
        positions = request.POST.getlist("position")
        born = request.POST.get("born", "")
        photo_url = request.POST.get("photo_url", "")
        nation = request.POST.get("nation", "")
        club = request.POST.get("club", "")
        id = unidecode(name).lower().replace(" ", "_")


        create_player(id, name, born, positions, photo_url, nation, club)

        return redirect("players")

    players_data = query_all_players() 

    # Filtering
    search_name = request.GET.get("name", "").strip().lower()
    position = request.GET.get("position", "").strip().lower()
    club = request.GET.get("club", "").strip().lower()
    nation = request.GET.get("nation", "").strip().lower()

    if search_name:
        players_data = [p for p in players_data if search_name in p["name"].lower()]
    if position:
        players_data = [p for p in players_data if position in [pos.lower() for pos in p["positions"]]]
    if club:
        players_data = [p for p in players_data if club in p["current_club"].lower()]
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

    nations = query_all_nations()
    clubs = query_all_clubs()

    return render(request, "players.html", {
        "entities_list": players_page,
        "search_name": search_name,
        "position": position,
        "club": club,
        "nation": nation,
        "nations": nations,
        "clubs": clubs,
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


def add_club_to_player(request, player_id):
    """
    Handle adding a new club to a player's history while maintaining past clubs.
    """
    if request.method == "POST":
        club_id = request.POST.get("club")

        if not club_id:
            return redirect("player", player_id=player_id)

        current_club = query_player_club(player_id)

        update_player_club(player_id, current_club, club_id)

        return redirect("player", player_id=player_id)
