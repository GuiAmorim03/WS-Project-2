from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils.sparql_client import add_new_player_position, query_player_club, query_player_details, query_club_details, query_club_players, query_all_players, query_all_clubs, query_graph_data, query_top_players_by_stat, query_top_clubs_by_stat, query_all_nations, create_player, update_player_club, check_player_connection, delete_player
from unidecode import unidecode

def player_detail(request, player_id):
    # Get player data from the SPARQL endpoint
    player_data = query_player_details(player_id)
    # Log the player data

    available_clubs = query_all_clubs()
    position_mapping = {
        "GK": "Goalkeeper",
        "DF": "Defender",
        "MF": "Midfielder",
        "FW": "Forward",
    }
    player_positions = set(player_data.get("raw_positions", []))
    available_positions = {key: value for key, value in position_mapping.items() if key not in player_positions}

    return render(request, "player.html", {
        "player_id": player_id,
        "entity": player_data, 
        "available_clubs": available_clubs,
        "available_positions": available_positions.items(),
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

def add_position_to_player(request, player_id):
    """
    Handle adding a new position to a player.
    """
    if request.method == "POST":
        position = request.POST.get("position")
        
        if not position:
            return redirect("player", player_id=player_id)

        add_new_player_position(player_id, position)

        # Redirect back to player detail page
        return redirect("player", player_id=player_id)

def player_connection_checker(request):
    """
    View for checking connections between two players using SPARQL ASK query
    """
    # Initialize variables
    results = None
    player_list = None
    player1_id = request.GET.get("player1")
    player2_id = request.GET.get("player2")
    
    # Get the list of all players for the selection dropdowns
    player_list = query_all_players()
    
    # If both players are selected, check connections
    if player1_id and player2_id:
        results = check_player_connection(player1_id, player2_id)
        
        # Get player details for the results display
        player1_data = query_player_details(player1_id)
        player2_data = query_player_details(player2_id)
        
        results["player1"] = {
            "id": player1_id,
            "name": player1_data["name"],
            "photo_url": player1_data["photo_url"],
            "color": player1_data["color"],           # Add color
            "alternate_color": player1_data["alternate_color"]  # Add alternate color
        }
        
        results["player2"] = {
            "id": player2_id,
            "name": player2_data["name"],
            "photo_url": player2_data["photo_url"],
            "color": player2_data["color"],           # Add color
            "alternate_color": player2_data["alternate_color"]  # Add alternate color
        }

        # Stats where the lower value is better (fouls commited, red cards, yellow cards, etc.)
        negative_stats = [
            "Errors Leading to Goal",
            "Miscontrols",
            "Times Dispossessed",
            "Goals Conceded",
            "Goals Conceded per 90 minutes",
            "Yellow Cards",
            "Red Cards",
            "Fouls Committed",
            "Penalties Conceded",
            "Own Goals",
            "Offsides",
        ]
        
        # Pre-process stats for comparison (no need for template filters)
        stats_comparison = []
        
        if "stats" in player1_data and "stats" in player2_data:
            # Create a map of player2's stats for quick lookup
            player2_stats_map = {}
            for category in player2_data["stats"]:
                cat_name = category["name"]
                player2_stats_map[cat_name] = {}
                for stat in category["stats"]:
                    player2_stats_map[cat_name][stat["name"]] = stat["value"]
            
            # Process each category from player1
            for category in player1_data["stats"]:
                cat_name = category["name"]
                comparison_category = {
                    "name": cat_name,
                    "stats": []
                }
                
                # Process each stat in this category
                for stat in category["stats"]:
                    stat_name = stat["name"]
                    player1_value = stat["value"]
                    # Get corresponding stat from player2 (default to 0 if not found)
                    player2_value = player2_stats_map.get(cat_name, {}).get(stat_name, 0)
                    
                    # Try to convert values to numbers for comparison
                    try:
                        p1_val = float(player1_value)
                        p2_val = float(player2_value)
                        
                        # Check if this is a negative stat (lower is better)
                        is_negative = stat_name in negative_stats
                        
                        if is_negative:
                            # For negative stats, lower values are better
                            player1_better = p1_val < p2_val
                            player2_better = p2_val < p1_val
                        else:
                            # For regular stats, higher values are better
                            player1_better = p1_val > p2_val
                            player2_better = p2_val > p1_val
                            
                        equal = p1_val == p2_val
                    except (ValueError, TypeError):
                        # If conversion fails, treat as strings
                        player1_better = False
                        player2_better = False
                        equal = player1_value == player2_value
                    
                    comparison_category["stats"].append({
                        "name": stat_name,
                        "player1_value": player1_value,
                        "player2_value": player2_value,
                        "player1_better": player1_better,
                        "player2_better": player2_better,
                        "equal": equal,
                        "is_negative": stat_name in negative_stats  # Include this flag for UI display
                    })
                
                stats_comparison.append(comparison_category)
            
            results["stats_comparison"] = stats_comparison
    
    return render(request, "player_connection.html", {
        "player_list": player_list,
        "results": results,
        "selected_player1": player1_id,
        "selected_player2": player2_id,
    })

def delete_player_view(request, player_id):
    """
    Handle deleting a player.
    """
    if request.method == "POST":
        # Delete the player using the delete_player function from sparql_client
        success = delete_player(player_id)
        if success:
            return redirect("players")  # Redirect to players list after deletion
    
    # If not a POST request or deletion failed, redirect back to player detail
    return redirect("player", player_id=player_id)
