from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .utils.sparql_client import add_new_player_position, query_player_club, query_player_details, query_club_details, query_club_players, query_all_players, query_all_clubs, query_graph_data, query_top_players_by_stat, query_top_clubs_by_stat, query_all_nations, create_player, update_player_club, check_player_connection, delete_player
from .utils.spin_client import (
    execute_spin_rules, clear_spin_inferences, query_enhanced_player_details, 
    query_enhanced_all_players, query_player_teammates, query_player_compatriots,
    query_players_by_classification, query_club_rivals, query_efficiency_leaders,
    check_enhanced_player_connection
)
from .utils.wikidata_client import query_club_details_extra, query_stadium_details, query_league_details, query_league_winners
from unidecode import unidecode

# Global variable to track SPIN rules state
SPIN_RULES_ACTIVE = False

def player_detail(request, player_id):
    # Get player data from the SPARQL endpoint
    if SPIN_RULES_ACTIVE:
        enhanced_data = query_enhanced_player_details(player_id)
        if enhanced_data:
            # Merge enhanced data with base player data
            player_data = query_player_details(player_id)
            player_data["spin_inferences"] = enhanced_data["spin_inferences"]
            
            # Add efficiency as a stat if available
            if "efficiency" in enhanced_data["spin_inferences"]:
                efficiency_value = enhanced_data["spin_inferences"]["efficiency"]
                
                # Find the Attacking category
                attacking_category = None
                for category in player_data["stats"]:
                    if category["name"] == "Attacking":
                        attacking_category = category
                        break
                
                if attacking_category:
                    # Check if efficiency stat already exists
                    efficiency_stat_exists = any(stat["name"] == "Efficiency" for stat in attacking_category["stats"])
                    if not efficiency_stat_exists:
                        # Add efficiency stat to the Attacking category with SPIN badge flag
                        attacking_category["stats"].append({
                            "name": "Efficiency",
                            "value": efficiency_value,
                            "is_spin_stat": True  # Flag to show SPIN badge
                        })
                    else:
                        # Update existing efficiency stat with spin stat
                        for stat in attacking_category["stats"]:
                            if stat["name"] == "Efficiency":
                                stat["is_spin_stat"] = True

            
            # Add SPIN rule related data
            player_data["teammates"] = query_player_teammates(player_id)
            player_data["compatriots"] = query_player_compatriots(player_id)
        else:
            player_data = query_player_details(player_id)
    else:
        player_data = query_player_details(player_id)

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
    
    # Add SPIN rule enhanced data if active
    if SPIN_RULES_ACTIVE:
        # Add rival clubs information
        rivals = query_club_rivals(club_id)
        club_data["rivals"] = rivals[:5]  # Show top 5 rivals
        club_data["has_rivals"] = len(rivals) > 0
    else:
        club_data["rivals"] = []
        club_data["has_rivals"] = False
    
    # Add SPIN rules status for template
    club_data["spin_rules_active"] = SPIN_RULES_ACTIVE
    
    # Log the club data
    print(club_data)
    
    return render(request, "club.html", {"entity": club_data})

def club_wikidata_details(request, club_id):
    """
    AJAX endpoint for fetching Wikidata details for a club.
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        # Get basic club data to extract the name
        club_data = query_club_details(club_id)
        club_name = club_data.get("name", "")
        
        if not club_name:
            return JsonResponse({'success': False, 'message': 'Club not found'})
        
        # Get club data from WikiData
        club_extra_data = query_club_details_extra(club_name)
        
        if club_extra_data:
            # Process the data for JSON response
            response_data = {
                'success': True,
                'data': {
                    'brands': club_extra_data.get('brands', []),
                    'official_name': club_extra_data.get('official_name'),
                    'nicknames': club_extra_data.get('nicknames', []),
                    'audio': club_extra_data.get('audio'),
                    'inception': club_extra_data.get('inception'),
                    'president': club_extra_data.get('president'),
                    'coach': club_extra_data.get('coach'),
                    'media_followers': club_extra_data.get('media_followers', 0),
                    'venue': club_extra_data.get('venue', {})
                }
            }
        else:
            response_data = {
                'success': False,
                'message': 'No Wikidata information found for this club'
            }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching Wikidata information: {str(e)}'
        })

def stadium_detail(request, stadium_id):
    # Get stadium data from the SPARQL endpoint
    stadium_data = query_stadium_details(stadium_id)

    return render(request, "stadium.html", {"entity": stadium_data})

def league_detail(request, league_name):
    # Get league data from the SPARQL endpoint
    league_data = query_league_details(league_name)

    league_winners = query_league_winners(league_data["id"])
    if league_winners:
        league_data["winners"] = league_winners

    return render(request, "league.html", {"entity": league_data})

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

    # Add SPIN rule enhanced data if active
    if SPIN_RULES_ACTIVE:
        # Add efficiency leaders section
        efficiency_leaders_data = query_efficiency_leaders(10)
        if efficiency_leaders_data and efficiency_leaders_data.get("entities"):
            stats[0]["stats"].insert(0, efficiency_leaders_data)

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

    # Use enhanced query if SPIN rules are active
    if SPIN_RULES_ACTIVE:
        players_data = query_enhanced_all_players()
        
        # Process enhanced data for template compatibility
        for player in players_data:
            # Calculate age from birth year if not available from SPIN rules
            if "current_age" not in player.get("spin_inferences", {}):
                birth_year = player["born"]
                current_year = 2025
                player["age"] = current_year - birth_year
            else:
                player["age"] = player["spin_inferences"]["current_age"]
            
            # Add SPIN inference badges for display with new styling
            player["spin_badges"] = []
            if player.get("spin_inferences"):
                inferences = player["spin_inferences"]
                
                # Age-based badges
                if inferences.get("is_veteran"):
                    player["spin_badges"].append({
                        "label": "Veteran", 
                        "class": "veteran with-icon",
                        "icon": "fas fa-crown"
                    })
                if inferences.get("is_young_prospect"):
                    player["spin_badges"].append({
                        "label": "Young Prospect", 
                        "class": "prospect with-icon",
                        "icon": "fas fa-star"
                    })
                
                # Role-based badges
                if inferences.get("is_key_player"):
                    player["spin_badges"].append({
                        "label": "Key Player", 
                        "class": "key-player with-icon",
                        "icon": "fas fa-key"
                    })
                if inferences.get("player_type"):
                    player_type = inferences["player_type"]
                    if player_type == "Striker":
                        player["spin_badges"].append({
                            "label": "Striker", 
                            "class": "goal-threat with-icon",
                            "icon": "fas fa-bullseye"
                        })
                    elif player_type == "Defensive Midfielder":
                        player["spin_badges"].append({
                            "label": "Def. Mid", 
                            "class": "secondary with-icon",
                            "icon": "fas fa-shield-alt"
                        })
                
                # Special abilities
                if inferences.get("is_playmaker"):
                    player["spin_badges"].append({
                        "label": "Playmaker", 
                        "class": "playmaker with-icon",
                        "icon": "fas fa-magic"
                    })
                if inferences.get("is_versatile"):
                    player["spin_badges"].append({
                        "label": "Versatile", 
                        "class": "versatile with-icon",
                        "icon": "fas fa-sync-alt"
                    })
                
                # Performance metrics
                if inferences.get("efficiency") and inferences["efficiency"] > 0.5:
                    player["spin_badges"].append({
                        "label": "High Efficiency", 
                        "class": "efficiency with-icon",
                        "icon": "fas fa-chart-line"
                    })
    else:
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
    
    # Add SPIN rule enhanced data if active
    if SPIN_RULES_ACTIVE:
        for club in clubs_data:
            # Add rival clubs information
            rivals = query_club_rivals(club["id"])
            club["rivals"] = rivals[:3]  # Show top 3 rivals

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
    if SPIN_RULES_ACTIVE:
        player_list = query_enhanced_all_players()
        # Format for template compatibility
        for player in player_list:
            player["positions"] = ", ".join(player["positions"])
    else:
        player_list = query_all_players()
    
    # If both players are selected, check connections
    if player1_id and player2_id:
        # Use enhanced connection checking if SPIN rules are active
        if SPIN_RULES_ACTIVE:
            enhanced_results = check_enhanced_player_connection(player1_id, player2_id)
            results = check_player_connection(player1_id, player2_id)
            
            # Merge enhanced connections
            if enhanced_results and enhanced_results.get("spin_connections"):
                results["spin_connections"] = enhanced_results["spin_connections"]
        else:
            results = check_player_connection(player1_id, player2_id)
        
        # Calculate connection status properly
        standard_connections_exist = any(conn["exists"] for conn in results["connections"].values())
        spin_connections_exist = False
        
        if SPIN_RULES_ACTIVE and results.get("spin_connections"):
            spin_connections_exist = any(conn["exists"] for conn in results["spin_connections"].values())
        
        # Update connection flags
        results["has_standard_connections"] = standard_connections_exist
        results["has_spin_connections"] = spin_connections_exist
        results["has_connection"] = standard_connections_exist or spin_connections_exist
        
        # Get player details for the results display
        player1_data = query_player_details(player1_id)
        player2_data = query_player_details(player2_id)
        
        # Add SPIN inference data if available
        if SPIN_RULES_ACTIVE:
            enhanced_player1 = query_enhanced_player_details(player1_id)
            enhanced_player2 = query_enhanced_player_details(player2_id)
            
            if enhanced_player1:
                player1_data["spin_inferences"] = enhanced_player1["spin_inferences"]
                
                # Add efficiency as a stat if available
                if "efficiency" in enhanced_player1["spin_inferences"]:
                    efficiency_value = enhanced_player1["spin_inferences"]["efficiency"]
                    
                    # Find the Attacking category
                    attacking_category = None
                    for category in player1_data["stats"]:
                        if category["name"] == "Attacking":
                            attacking_category = category
                            break
                    
                    efficiency_stat_exists = any(stat["name"] == "Efficiency" for stat in attacking_category["stats"])
                    if not efficiency_stat_exists:
                        # Add efficiency stat to the Attacking category with SPIN badge flag
                        attacking_category["stats"].append({
                            "name": "Efficiency",
                            "value": efficiency_value,
                            "is_spin_stat": True  # Flag to show SPIN badge
                        })
                    else:
                        # Update existing efficiency stat with spin stat
                        for stat in attacking_category["stats"]:
                            if stat["name"] == "Efficiency":
                                stat["is_spin_stat"] = True
                        
            if enhanced_player2:
                player2_data["spin_inferences"] = enhanced_player2["spin_inferences"]
                
                # Add efficiency as a stat if available
                if "efficiency" in enhanced_player2["spin_inferences"]:
                    efficiency_value = enhanced_player2["spin_inferences"]["efficiency"]
                    
                    # Find the Attacking category
                    attacking_category = None
                    for category in player2_data["stats"]:
                        if category["name"] == "Attacking":
                            attacking_category = category
                            break
                    
                    efficiency_stat_exists = any(stat["name"] == "Efficiency" for stat in attacking_category["stats"])
                    if not efficiency_stat_exists:
                        # Add efficiency stat to the Attacking category with SPIN badge flag
                        attacking_category["stats"].append({
                            "name": "Efficiency",
                            "value": efficiency_value,
                            "is_spin_stat": True  # Flag to show SPIN badge
                        })
                    else:
                        # Update existing efficiency stat with spin stat
                        for stat in attacking_category["stats"]:
                            if stat["name"] == "Efficiency":
                                stat["is_spin_stat"] = True
            
            # Check for SPIN property connections
            if enhanced_player1 and enhanced_player2:
                spin_property_connections = check_spin_property_connections(
                    enhanced_player1["spin_inferences"],
                    enhanced_player2["spin_inferences"]
                )
                
                # Add SPIN property connections to results
                if not results.get("spin_connections"):
                    results["spin_connections"] = {}
                
                results["spin_connections"].update(spin_property_connections)
                
                # Update connection flags
                spin_property_exists = any(conn["exists"] for conn in spin_property_connections.values())
                results["has_spin_connections"] = results.get("has_spin_connections", False) or spin_property_exists
                results["has_connection"] = results["has_connection"] or spin_property_exists
        
        results["player1"] = {
            "id": player1_id,
            "name": player1_data["name"],
            "photo_url": player1_data["photo_url"],
            "color": player1_data["color"],
            "alternate_color": player1_data["alternate_color"],
            "spin_inferences": player1_data.get("spin_inferences", {})
        }
        
        results["player2"] = {
            "id": player2_id,
            "name": player2_data["name"],
            "photo_url": player2_data["photo_url"],
            "color": player2_data["color"],
            "alternate_color": player2_data["alternate_color"],
            "spin_inferences": player2_data.get("spin_inferences", {})
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
                    
                    # Check if this is a SPIN-derived stat
                    is_spin_stat = "efficiency" in stat_name.lower()
                    
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
                        "is_negative": stat_name in negative_stats,
                        "is_spin_stat": is_spin_stat
                    })
                
                stats_comparison.append(comparison_category)
            
            results["stats_comparison"] = stats_comparison
    
    return render(request, "player_connection.html", {
        "player_list": player_list,
        "results": results,
        "selected_player1": player1_id,
        "selected_player2": player2_id,
        "spin_rules_active": SPIN_RULES_ACTIVE,
    })

def check_spin_property_connections(player1_inferences, player2_inferences):
    """
    Check if two players share SPIN rule properties.
    
    Args:
        player1_inferences: SPIN inferences for player 1
        player2_inferences: SPIN inferences for player 2
        
    Returns:
        dict: SPIN property connections
    """
    connections = {}
    
    # Check for shared boolean properties
    boolean_properties = [
        ("is_veteran", "Both are Veterans"),
        ("is_young_prospect", "Both are Young Prospects"),
        ("is_key_player", "Both are Key Players"),
        ("is_playmaker", "Both are Playmakers"),
        ("is_goal_threat", "Both are Goal Threats"),
        ("is_penalty_specialist", "Both are Penalty Specialists"),
        ("is_versatile", "Both are Versatile Players"),
        ("is_disciplinary_risk", "Both are Disciplinary Risks")
    ]
    
    for prop, description in boolean_properties:
        player1_has = player1_inferences.get(prop, False)
        player2_has = player2_inferences.get(prop, False)
        
        connections[f"both_{prop}"] = {
            "exists": player1_has and player2_has,
            "description": f"Connected via SPIN rule: {description}"
        }
    
    # Check for same player type
    player1_type = player1_inferences.get("player_type")
    player2_type = player2_inferences.get("player_type")
    
    connections["same_player_type"] = {
        "exists": player1_type and player2_type and player1_type == player2_type,
        "description": f"Connected via SPIN rule: Same Player Type ({player1_type})" if player1_type and player2_type and player1_type == player2_type else "Connected via SPIN rule: Same Player Type"
    }
    
    # Check for similar efficiency (within 0.1 range)
    player1_eff = player1_inferences.get("efficiency")
    player2_eff = player2_inferences.get("efficiency")
    
    if player1_eff and player2_eff:
        efficiency_similar = abs(player1_eff - player2_eff) <= 0.1
        connections["similar_efficiency"] = {
            "exists": efficiency_similar,
            "description": f"Connected via SPIN rule: Similar Efficiency ({player1_eff:.3f} vs {player2_eff:.3f})"
        }
    
    return connections

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

def toggle_spin_rules(request):
    """
    Toggle SPIN rules activation state and execute/clear rules accordingly.
    """
    global SPIN_RULES_ACTIVE
    
    if request.method == "POST":
        SPIN_RULES_ACTIVE = not SPIN_RULES_ACTIVE
        
        try:
            if SPIN_RULES_ACTIVE:
                # Execute SPIN rules
                success = execute_spin_rules()
                if success:
                    message = "SPIN rules activated and executed successfully"
                else:
                    # Rollback state if execution failed
                    SPIN_RULES_ACTIVE = False
                    message = "Failed to execute SPIN rules"
                    return JsonResponse({
                        'success': False,
                        'spin_rules_active': SPIN_RULES_ACTIVE,
                        'message': message
                    })
            else:
                # Clear SPIN rule inferences
                success = clear_spin_inferences()
                if success:
                    message = "SPIN rules deactivated and inferences cleared"
                else:
                    # Rollback state if clearing failed
                    SPIN_RULES_ACTIVE = True
                    message = "Failed to clear SPIN rule inferences"
                    return JsonResponse({
                        'success': False,
                        'spin_rules_active': SPIN_RULES_ACTIVE,
                        'message': message
                    })
            
            return JsonResponse({
                'success': True,
                'spin_rules_active': SPIN_RULES_ACTIVE,
                'message': message
            })
            
        except Exception as e:
            # Rollback state on any exception
            SPIN_RULES_ACTIVE = not SPIN_RULES_ACTIVE
            return JsonResponse({
                'success': False,
                'spin_rules_active': SPIN_RULES_ACTIVE,
                'message': f"Error toggling SPIN rules: {str(e)}"
            })
    
    elif request.method == "GET":
        # Return the current status of SPIN rules
        return JsonResponse({
            'success': True,
            'spin_rules_active': SPIN_RULES_ACTIVE,
            'message': 'Current SPIN rules status retrieved successfully'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })