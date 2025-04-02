from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from datetime import datetime

from .sparql_queries import (
    get_player_details_query, get_club_details_query, get_club_players_query,
    get_all_players_query, get_all_clubs_query, get_player_stats_query,
    get_club_stats_query, get_graph_data_query, get_top_players_by_stat_query,
    get_top_clubs_by_stat_query, get_player_club_query, get_update_player_club_query,
    get_all_nations_query, get_create_player_query, get_add_player_position_query,
    get_player_connection_query, get_delete_player_query
)

# Configure your SPARQL endpoint
ENDPOINT_URL = "http://graphdb:7200/repositories/football"  # Replace with your actual endpoint URL

def get_sparql_client():
    """Returns a configured SPARQLWrapper instance."""
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setReturnFormat(JSON)
    return sparql

def process_query(query, process_func=None, additional_process_params=None, error_message=None, success_message=None):
    """
    Execute a SPARQL query and return the results.
    
    Args:
        query: The SPARQL query string to execute
        method: HTTP method to use (GET or POST)
    """

    sparql = get_sparql_client()
    sparql.setQuery(query)
    
    try:
        results = sparql.query().convert()
        if process_func:
            if additional_process_params:
                return process_func(results, **additional_process_params)
            return process_func(results)
        if success_message:
            print(success_message)
        return results
    except Exception as e:
        if error_message:
            print(f"{error_message}: {e}")
        else:   
            print(f"SPARQL query error: {e}")
        return None

def query_player_details(player_id):
    """
    Query and process player details from the SPARQL endpoint.
    
    Args:
        player_id: The ID of the player to query
        
    Returns:
        dict: Processed player data ready for template rendering
    """
    
    return process_query(get_player_details_query(player_id), process_func=process_player_results, additional_process_params={"player_id": player_id}
                         , error_message="Error querying player details", success_message="Player details queried successfully")

def process_player_results(results, player_id):
    """Process the SPARQL query results into the format needed for templates."""
    if not results["results"]["bindings"]:
        return get_default_player_data()
    
    result = results["results"]["bindings"][0]
    
    # Position mapping dictionary
    position_mapping = {
        "GK": "Goalkeeper",
        "DF": "Defender",
        "MF": "Midfielder",
        "FW": "Forward",
    }
    
    # Extract positions from comma-separated string
    positions_str = result.get("positions", {}).get("value", "")
    raw_positions = [pos.strip() for pos in positions_str.split(",")] if positions_str else []
    print(raw_positions) 
    # Convert abbreviated positions to full names
    positions = []
    for pos in raw_positions:
        if pos in position_mapping:
            positions.append(f"{position_mapping[pos]} ({pos})")
        else:
            positions.append(pos)
    
    # Extract past clubs
    past_clubs_str = result.get("pastClubs", {}).get("value", "")
    past_clubs_names_str = result.get("pastClubNames", {}).get("value", "")
    past_clubs_logos_str = result.get("pastClubLogos", {}).get("value", "")
    
    past_clubs = past_clubs_str.split(", ") if past_clubs_str else []
    past_clubs_names = past_clubs_names_str.split(", ") if past_clubs_names_str else []
    past_clubs_logos = past_clubs_logos_str.split(", ") if past_clubs_logos_str else []
    
    teams = []
    # Add current club
    teams.append({
        "id": result["currentClub"]["value"].split("/")[-1],
        "name": result["currentClubName"]["value"],
        "logo": result["currentClubLogo"]["value"],
    })
    
    # Add past clubs
    for i in range(len(past_clubs)):
        club_id = past_clubs[i].split("/")[-1]
        club_name = past_clubs_names[i] if i < len(past_clubs_names) else ""
        club_logo = past_clubs_logos[i] if i < len(past_clubs_logos) else ""
        teams.append({
            "id": club_id,
            "name": club_name,
            "logo": club_logo
        })
    
    # Calculate age
    birth_year = int(result["born"]["value"])
    current_year = datetime.now().year
    age = current_year - birth_year
    
    return {
        "name": result["name"]["value"],
        "born": birth_year,
        "age": age,
        "photo_url": result["photo_url"]["value"],
        "pos": positions,
        "country_name": result["nation"]["value"].split("/")[-1].replace("_", " ").title(),
        "flag": result["flag"]["value"],
        "clubs": teams,
        "color": result["currentClubColor"]["value"],
        "alternate_color": result["currentClubAltColor"]["value"],
        "stats": query_player_stats(player_id),
        "raw_positions": raw_positions
    }

def get_default_player_data():
    """Return default player data for when no results are found."""
    return {
        "name": "Player Not Found",
        "born": 0,
        "age": 0,
        "pos": [],
        "country_name": "",
        "flag": "",
        "teams": [],
        "color": "000000",
        "alternate_color": "FFFFFF",
        "stats": []
    }

def query_club_details(club_id):
    """
    Query and process club details from the SPARQL endpoint.
    
    Args:
        club_id: The ID of the club to query
        
    Returns:
        dict: Processed club data ready for template rendering
    """
    
    return process_query(get_club_details_query(club_id), process_func=process_club_results, additional_process_params={"club_id": club_id}, 
                         error_message="Error querying club details", success_message="Club details queried successfully")

def process_club_results(results, club_id):
    """Process the SPARQL query results for club details into the format needed for templates."""
    if not results["results"]["bindings"]:
        return get_default_club_data()
    
    result = results["results"]["bindings"][0]
    
    return {
        "id": result["club_id"]["value"].split("/")[-1],
        "name": result["name"]["value"],
        "abbreviation": result["abbreviation"]["value"],
        "stadium": result["stadium"]["value"],
        "city": result["city"]["value"],
        "league": {
            "id": result["league_id"]["value"].split("/")[-1],
            "name": result["league_name"]["value"]
        },
        "country": {
            "flag": result["flag"]["value"]
        },
        "logo": result["logo"]["value"],
        "color": result["color"]["value"],
        "alternate_color": result["alternateColor"]["value"],
        "stats": query_club_stats(club_id),
    }

def get_default_club_data():
    """Return default club data for when no results are found."""
    return {
        "id": "",
        "name": "Club Not Found",
        "abbreviation": "",
        "stadium": "",
        "city": "",
        "league": {
            "id": "",
            "name": ""
        },
        "country": {
            "flag": ""
        },
        "logo": "",
        "color": "000000",
        "alternate_color": "FFFFFF"
    }

def query_club_players(club_id):
    """
    Query and process a club's players from the SPARQL endpoint.
    
    Args:
        club_id: The ID of the club to query players for
        
    Returns:
        list: List of processed player data ready for template rendering
    """
    
    return process_query(get_club_players_query(club_id), process_func=process_club_players_results,
                         error_message="Error querying club players", success_message="Club players queried successfully")

def process_club_players_results(results):
    """Process the SPARQL query results for club players into the format needed for templates."""
    if not results["results"]["bindings"]:
        return []
    
    players = []
    for player in results["results"]["bindings"]:
        # Extract positions from comma-separated string
        positions_str = player.get("positions", {}).get("value", "")
        positions = [pos.strip() for pos in positions_str.split(",")] if positions_str else []
        
        # Calculate age
        birth_year = int(player["born"]["value"])
        current_year = datetime.now().year
        age = current_year - birth_year
        
        players.append({
            "id": player["player_id"]["value"].split("/")[-1],
            "name": player["name"]["value"],
            "born": birth_year,
            "age": age,
            "photo_url": player["photo_url"]["value"],
            "positions": positions,
            "nation": player["nation"]["value"],
            "flag": player["flag"]["value"]
        })
    
    return players

def query_all_players():
    """
    Query and process a list of all players from the SPARQL endpoint.
    
    Returns:
        list: List of processed player data ready for template rendering
    """
    
    return process_query(get_all_players_query(), process_func=process_all_players_results,
                         error_message="Error querying all players", success_message="All players queried successfully")

def process_all_players_results(results):
    """Process the SPARQL query results for all players into the format needed for templates."""
    if not results["results"]["bindings"]:
        return []
    
    players = []
    for player in results["results"]["bindings"]:
        # Extract positions from comma-separated string
        positions_str = player.get("positions", {}).get("value", "")
        positions = [pos.strip() for pos in positions_str.split(",")] if positions_str else []
        
        # Calculate age
        birth_year = int(player["born"]["value"])
        current_year = datetime.now().year
        age = current_year - birth_year
        
        # Extract player ID from URI
        player_id = player["player_id"]["value"].split("/")[-1]
        
        # Handle optional current club information
        current_club = None
        current_club_logo = None
        
        if "currentClubName" in player and player["currentClubName"]["value"]:
            current_club = player["currentClubName"]["value"].split("/")[-1]
            
        if "currentClubLogo" in player and player["currentClubLogo"]["value"]:
            current_club_logo = player["currentClubLogo"]["value"]
           
        # print(player)
        players.append({
            "id": player_id,
            "name": player["name"]["value"],
            "born": birth_year,
            "age": age,
            "positions": positions,
            "nation": player["nation"]["value"],
            "flag": player["flag"]["value"],
            "current_club": current_club,
            "club_logo": current_club_logo
        })
    
    return players

def query_all_clubs():
    """
    Query and process a list of all clubs from the SPARQL endpoint.
    
    Returns:
        list: List of processed club data ready for template rendering
    """

    return process_query(get_all_clubs_query(), process_func=process_all_clubs_results, 
                         error_message="Error querying all clubs", success_message="All clubs queried successfully")

def process_all_clubs_results(results):
    """Process the SPARQL query results for all clubs into the format needed for templates."""
    if not results["results"]["bindings"]:
        return []
    
    clubs = []
    for club in results["results"]["bindings"]:
        # Extract club ID from URI
        club_id = club["club_id"]["value"].split("/")[-1]
        
        # Get number of players (convert to integer)
        num_players = int(club.get("numPlayers", {}).get("value", "0"))
        
        clubs.append({
            "id": club_id,
            "name": club["name"]["value"],
            "abbreviation": club["abbreviation"]["value"],
            "league": club["league"]["value"],
            "flag": club["flag"]["value"],
            "logo": club["logo"]["value"],
            "color": club["color"]["value"],
            "alternate_color": club["alternateColor"]["value"],
            "num_players": num_players
        })
    
    return clubs

def query_player_stats(player_id):
    """
    Query and process player statistics from the SPARQL endpoint.
    
    Args:
        player_id: The ID of the player to query stats for
        
    Returns:
        list: List of processed stats categories ready for template rendering
    """
    
    return process_query(get_player_stats_query(player_id), process_func=process_player_stats_results,
                         error_message="Error querying player stats", success_message="Player stats queried successfully")

def process_player_stats_results(results):
    """
    Process the SPARQL query results for player stats into the format needed for templates.
    Stats are grouped by category.
    """
    if not results["results"]["bindings"]:
        return []
    
    # Create a dictionary to group stats by category
    categories = {}
    
    for stat in results["results"]["bindings"]:
        category = stat["stat_category"]["value"]
        stat_name = stat["stat_name"]["value"]
        stat_value = stat["stat_value"]["value"]
        
        # Create category if it doesn't exist yet
        if category not in categories:
            categories[category] = {
                "name": category,
                "stats": []
            }
            
        # Add stat to the appropriate category
        categories[category]["stats"].append({
            "name": stat_name,
            "value": stat_value
        })
    
    return sort_stats_categories(categories)

def query_club_stats(club_id):
    """
    Query and process club statistics from the SPARQL endpoint.
    
    Args:
        club_id: The ID of the club to query stats for
        
    Returns:
        list: List of processed stats categories ready for template rendering
    """
    
    return process_query(get_club_stats_query(club_id), process_func=process_club_stats_results,
                         error_message="Error querying club stats", success_message="Club stats queried successfully")

def process_club_stats_results(results):
    """
    Process the SPARQL query results for club stats into the format needed for templates.
    Stats are grouped by category.
    """
    if not results["results"]["bindings"]:
        return []
    
    # Create a dictionary to group stats by category
    categories = {}
    
    for stat in results["results"]["bindings"]:
        category = stat["stat_category"]["value"]
        stat_name = stat["stat_name"]["value"]
        stat_value = stat["stat_value"]["value"]
        
        # If the stat value is a float, round it to 2 decimal places
        if '.' in stat_value:
            try:
                stat_value = round(float(stat_value), 2)
            except ValueError:
                pass
        
        # Create category if it doesn't exist yet
        if category not in categories:
            categories[category] = {
                "name": category,
                "stats": []
            }
            
        # Add stat to the appropriate category
        categories[category]["stats"].append({
            "name": stat_name,
            "value": stat_value
        })
    
    return sort_stats_categories(categories)

def query_graph_data(selected_node_id=None):
    """
    Query the RDF graph structure, returning nodes and relationships
    that can be visualized in a graph representation.
    
    Args:
        selected_node_id (str, optional): If provided, only return this node
            and its directly connected nodes (adjacent nodes)
    
    Returns:
        dict: Contains 'nodes' and 'links' for graph visualization
    """
    
    results = process_query(get_graph_data_query(selected_node_id),
                            error_message="Error querying graph data", success_message="Graph data queried successfully")
    
    # Process the results to create a graph structure
    nodes = {}
    links = []
    
    # Correctly iterate through the bindings in results
    for result in results["results"]["bindings"]:
        subject_uri = result.get('subject', {}).get('value', '')
        object_uri = result.get('object', {}).get('value', '')
        predicate = result.get('predicate', {}).get('value', '')
        
        # Use labels if available, otherwise use URIs
        subject_label = result.get('subjectLabel', {}).get('value', '') or subject_uri.split('/')[-1]
        object_label = result.get('objectLabel', {}).get('value', '') or object_uri.split('/')[-1]
        
        # Add subject node if not already added
        if subject_uri not in nodes:
            nodes[subject_uri] = {
                'id': subject_uri,
                'label': subject_label,
                'type': result.get('subjectType', {}).get('value', 'Unknown').split('#')[-1]
            }
        
        # Add object node if not already added and it's a URI (not a literal)
        if object_uri.startswith('http') and object_uri not in nodes:
            nodes[object_uri] = {
                'id': object_uri,
                'label': object_label,
                'type': result.get('objectType', {}).get('value', 'Unknown').split('#')[-1]
            }
        
        # Add relationship if object is a URI (not a literal)
        if object_uri.startswith('http'):
            links.append({
                'source': subject_uri,
                'target': object_uri,
                'label': predicate.split('/')[-1]
            })
    
    return {
        'nodes': list(nodes.values()),
        'links': links
    }

def sort_stats_categories(categories):
    category_order = {
        "Playing Time": 0,
        "Attacking": 1,
        "Defending": 2,
        "Passing & Creativity": 3,
        "Goalkeeping": 4,
        "Miscellaneous": 5
    }

    stat_orders = {
        "Playing Time": [
            "Matches Played", "Games Started", "Minutes Played"
        ],
        "Attacking": [
            "Goals", "Assists", "Goals + Assists", "Expected Goals",
            "Expected Assists", "Penalties Scored", "Penalties Attempted"
        ],
        "Defending": [
            "Tackles", "Tackles Won", "Blocks", "Interceptions",
            "Clearances", "Errors Leading to Goal", "Ball Recoveries"
        ],
        "Passing & Creativity": [
            "Progressive Passes", "Progressive Carries", "Progressive Runs",
            "Key Passes", "Passes into Penalty Area", "Total Passes",
            "Passes Completed", "Touches", "Miscontrols", "Times Dispossessed"
        ],
        "Goalkeeping": [
            "Goals Conceded", "Goals Conceded per 90 minutes", "Saves",
            "Save %", "Clean Sheets", "Clean Sheet %", "Penalties Faced", "Penalties Saved"
        ],
        "Miscellaneous": [
            "Yellow Cards", "Red Cards", "Fouls Committed", "Penalties Conceded",
            "Penalties Won", "Own Goals", "Offsides"
        ]
    }

    sorted_categories = sorted(
        categories.values(),
        key=lambda x: category_order.get(x["name"], float('inf'))
    )

    for category in sorted_categories:
        category_name = category["name"]
        if category_name in stat_orders:
            category["stats"].sort(key=lambda stat: stat_orders[category_name].index(stat["name"])
                                   if stat["name"] in stat_orders[category_name] else float('inf'))

    return sorted_categories

def query_top_players_by_stat(stat_id, limit=10):
    """
    Query and process top players for a specific stat from the SPARQL endpoint.
    
    Args:
        stat_id: The ID of the stat to query (e.g., "min" for minutes played)
        limit: Maximum number of players to return (default: 10)
        
    Returns:
        list: List of players with the specified stat, ordered by stat value
    """

    return process_query(get_top_players_by_stat_query(stat_id, limit), process_func=process_top_players_results,
                         error_message="Error querying top players by stat", success_message="Top players by stat queried successfully")

def process_top_players_results(results):
    """Process the SPARQL query results for top players into the format needed for templates."""
    if not results["results"]["bindings"]:
        return []
    
    stat_name = results["results"]["bindings"][0]["stat_name"]["value"]
    color = results["results"]["bindings"][0]["color"]["value"]
    alternate_color = results["results"]["bindings"][0]["alternateColor"]["value"] if color == 'ffffff' else 'ffffff'
    border = color if color != 'ffffff' else alternate_color
    
    players = []
    for player in results["results"]["bindings"]:
        # Extract player ID from URI
        player_id = player["player_id"]["value"].split("/")[-1]
        
        # Format stat value (convert to appropriate type if needed)
        stat_value = player["stat_value"]["value"]
        try:
            # Try to convert to float if it's a number
            stat_value = float(stat_value)
            # Format to 2 decimal places if it's a float
            if stat_value == int(stat_value):
                stat_value = int(stat_value)
            else:
                stat_value = round(stat_value, 2)
        except ValueError:
            # Keep as string if not a number
            pass
        
        players.append({
            "id": player_id,
            "name": player["name"]["value"],
            # "stat_name": player["stat_name"]["value"],
            "stat": stat_value,
            "info": player.get("club_name", {}).get("value", ""),
            # "club_logo": player.get("club_logo", {}).get("value", ""),
            # "flag": player.get("flag", {}).get("value", ""),
            "icon": player.get("photo_url", {}).get("value", "")
        })
    
    return {
        "name": stat_name,
        "colors": {
            "main": color,
            "alternate": alternate_color,
            "border": border,
        },
        "entities": players
    }

def query_top_clubs_by_stat(stat_id, limit=10):
    """
    Query and process top clubs for a specific stat from the SPARQL endpoint.
    
    Args:
        stat_id: The ID of the stat to query (e.g., "crdr" for cards red)
        limit: Maximum number of clubs to return (default: 10)
        
    Returns:
        list: List of clubs with the specified stat, ordered by stat value
    """

    return process_query(get_top_clubs_by_stat_query(stat_id, limit), process_func=process_top_clubs_results,
                         error_message="Error querying top clubs by stat", success_message="Top clubs by stat queried successfully")

def process_top_clubs_results(results):
    """Process the SPARQL query results for top clubs into the format needed for templates."""
    if not results["results"]["bindings"]:
        return []
    
    stat_name = results["results"]["bindings"][0]["stat_name"]["value"]
    color = results["results"]["bindings"][0]["color"]["value"]
    alternate_color = results["results"]["bindings"][0]["alternateColor"]["value"] if color == 'ffffff' else 'ffffff'
    border = color if color != 'ffffff' else alternate_color

    clubs = []
    for club in results["results"]["bindings"]:
        # Extract club ID from URI
        club_id = club["club_id"]["value"].split("/")[-1]
        
        # Format stat value (convert to appropriate type if needed)
        stat_value = club["stat_value"]["value"]
        try:
            # Try to convert to float if it's a number
            stat_value = float(stat_value)
            # Format to 2 decimal places if it's a float
            if stat_value == int(stat_value):
                stat_value = int(stat_value)
            else:
                stat_value = round(stat_value, 2)
        except ValueError:
            # Keep as string if not a number
            pass
        
        clubs.append({
            "id": club_id,
            "name": club["name"]["value"],
            # "stat_name": club["stat_name"]["value"],
            "stat": stat_value,
            "icon": club.get("logo", {}).get("value", ""),
            # "flag": club.get("flag", {}).get("value", ""),
            "info": club.get("league_name", {}).get("value", ""),
            # "color": club.get("color", {}).get("value", ""),
            # "alternate_color": club.get("alternateColor", {}).get("value", "")
        })
    
    return {
        "name": stat_name,
        "colors": {
            "main": color,
            "alternate": alternate_color,
            "border": border,
        },
        "entities": clubs
    }

def query_player_club(player_id):
        
        current_club = None

        results = process_query(get_player_club_query(player_id))
        result = results["results"]["bindings"][0]
        if result:
            current_club = result["currentClub"]["value"]

        return current_club

def update_player_club(player_id, current_club, club_id):
    """
    Update a player's club in the RDF graph.
    
    Args:
        player_id: ID of the player to update
        current_club: URI of the player's current club (to be moved to past clubs)
        club_id: ID of the player's new club
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    sparql = SPARQLWrapper(ENDPOINT_URL+"/statements")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)
    
    # Get the SPARQL update query from the query generator
    query = get_update_player_club_query(player_id, current_club, club_id)
    
    try:
        sparql.setQuery(query)
        sparql.query()
        print(f"Player club updated successfully.")
        return True
    except Exception as e:
        print(f"Error updating player club: {e}")
        return False

def query_all_nations():
    """
    Query and process a list of all nations from the SPARQL endpoint.
    
    Returns:
        list: List of all nations with name, flag, and ID"
        """
    
    return process_query(get_all_nations_query(), process_func=process_all_nations_results,
                            error_message="Error querying all nations", success_message="All nations queried successfully")
    
def process_all_nations_results(results):
    """Process the SPARQL query results for all nations into the format needed for templates."""
    if not results["results"]["bindings"]:
        return []
    
    nations = []
    for nation in results["results"]["bindings"]:

        nation_id = nation["abrv"]["value"]
        
        nations.append({
            "id": nation_id,
            "name": nation["name"]["value"],
        })
    
    return nations

def create_player(id, name, born, positions, photo_url, nation, club):
    """
    Create a new player in the RDF graph.
    
    Args:
        id: Player's unique identifier
        name: Player's name
        born: Year of birth
        positions: List of positions
        photo_url: URL of the player's photo
        nation: Nation URI
        club: Club ID
        
    Returns:
        bool: True if creation was successful, False otherwise
    """
    sparql = SPARQLWrapper(ENDPOINT_URL+"/statements")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)
    
    # Construct the URIs
    player_uri = f"http://football.org/ent/{id}"
    club_uri = f"http://football.org/ent/{club}"
    nation_uri = nation
    
    # Determine stat types based on player position
    PLAYER = "player"
    GK = "goalkeeper"
    main_position = GK if "GK" in positions else PLAYER
    
    # Define the statistics that apply to each position type
    stats = {
        "MP": [PLAYER, GK],
        "Starts": [PLAYER, GK],
        "Min": [PLAYER, GK],
        
        "Gls": [PLAYER, GK],
        "Ast": [PLAYER, GK],
        "G_plus_A": [PLAYER, GK],
        "xG": [PLAYER, GK],
        "xAG": [PLAYER, GK],
        "PK": [PLAYER, GK],
        "PKatt": [PLAYER, GK],

        "Tkl": [PLAYER],
        "TklW": [PLAYER],
        "Blocks_stats_defense": [PLAYER],
        "Int": [PLAYER],
        "Clr": [PLAYER],
        "Err": [PLAYER],
        "Recov": [PLAYER],

        "PrgP": [PLAYER],
        "PrgC": [PLAYER],
        "PrgR": [PLAYER],
        "KP": [PLAYER],
        "PPA": [PLAYER],
        "Live": [PLAYER],
        "Cmp_stats_passing_types": [PLAYER],
        "Touches": [PLAYER],
        "Mis": [PLAYER],
        "Dis": [PLAYER],

        "GA": [GK],
        "GA90": [GK],
        "Saves": [GK],
        "Save_pct": [GK],
        "CS": [GK],
        "CS_pct": [GK],
        "PKA": [GK],
        "PKsv": [GK],

        "CrdY": [PLAYER, GK],
        "CrdR": [PLAYER, GK],
        "Fls": [PLAYER, GK],
        "PKcon": [PLAYER, GK],
        "PKwon": [PLAYER, GK],
        "OG": [PLAYER, GK],
        "Off_stats_misc": [PLAYER, GK]
    }

    stats_filtered = [stat for stat, types in stats.items() if main_position in types]
    
    # Construct the stats statements
    stats_statements = ""
    for i, stat in enumerate(stats_filtered):
        final_mark = "." if i == len(stats_filtered) - 1 else ";"
        stats_statements += f"""            fut-stat:{stat.lower()} 0 {final_mark}
        """
    
    # Get the SPARQL create query using the query generator
    query = get_create_player_query(
        player_uri=player_uri,
        name=name,
        born=born,
        positions=positions,
        photo_url=photo_url,
        nation_uri=nation_uri,
        club_uri=club_uri, 
        stats_statements=stats_statements
    )
    
    try:
        sparql.setQuery(query)
        sparql.query()
        print(f"Player {name} created successfully.")
        return True
    except Exception as e:
        print(f"Error creating player: {e}")
        return False

def add_new_player_position(player_id, position):
    sparql = SPARQLWrapper(ENDPOINT_URL+"/statements")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)

    sparql.setQuery(get_add_player_position_query(player_id, position))

    try:
        sparql.query()
        print(f"New position created successfully.")
    except Exception as e:
        print(f"Error creating updating position: {e}")
        return False
    return True

def check_player_connection(player1_id, player2_id):
    """
    Check if two players have a connection using SPARQL ASK queries.
    
    Args:
        player1_id: ID of the first player
        player2_id: ID of the second player
        
    Returns:
        dict: Connection details with type and existence status
    """
    connections = {}
    
    # Check if they played for the same club (current or past)
    connections["same_club"] = {
        "exists": check_same_club_connection(player1_id, player2_id),
        "description": "Played for the same club"
    }
    
    # Check if they are from the same country
    connections["same_country"] = {
        "exists": check_same_country_connection(player1_id, player2_id),
        "description": "Come from the same country"
    }
    
    # Check if they play the same position
    connections["same_position"] = {
        "exists": check_same_position_connection(player1_id, player2_id),
        "description": "Play the same position"
    }
    
    # Summary of connections
    any_connection = any(conn["exists"] for conn in connections.values())
    
    return {
        "player1_id": player1_id,
        "player2_id": player2_id,
        "has_connection": any_connection,
        "connections": connections
    }

def check_same_club_connection(player1_id, player2_id):
    """Check if two players have played for the same club (current or past)."""
    sparql = get_sparql_client()
    
    sparql.setQuery(get_player_connection_query("same_club", player1_id, player2_id))

    try:
        return sparql.query().convert()["boolean"]
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return False

def check_same_country_connection(player1_id, player2_id):
    """Check if two players are from the same country."""
    sparql = get_sparql_client()
    
    
    sparql.setQuery(get_player_connection_query("same_country", player1_id, player2_id))

    try:
        return sparql.query().convert()["boolean"]
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return False

def check_same_position_connection(player1_id, player2_id):
    """Check if two players play the same position."""
    sparql = get_sparql_client()

    sparql.setQuery(get_player_connection_query("same_position", player1_id, player2_id))

    try:
        return sparql.query().convert()["boolean"]
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return False

def delete_player(player_id):
    """
    Delete a player and all their connections from the RDF graph.
    
    Args:
        player_id: The ID of the player to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    sparql = SPARQLWrapper(ENDPOINT_URL+"/statements")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)
    
    sparql.setQuery(get_delete_player_query(player_id))

    try:
        sparql.query()
        print(f"Player {player_id} deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting player: {e}")
        return False