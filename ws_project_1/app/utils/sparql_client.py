from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

# Configure your SPARQL endpoint
ENDPOINT_URL = "http://graphdb:7200/repositories/football"  # Replace with your actual endpoint URL

def get_sparql_client():
    """Returns a configured SPARQLWrapper instance."""
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setReturnFormat(JSON)
    return sparql

def query_player_details(player_id):
    """
    Query and process player details from the SPARQL endpoint.
    
    Args:
        player_id: The ID of the player to query
        
    Returns:
        dict: Processed player data ready for template rendering
    """
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?player_id
        ?name
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?nation
        ?flag
        ?currentClub
        ?currentClubName
        ?currentClubLogo
        ?currentClubColor
        ?currentClubAltColor
        (GROUP_CONCAT(DISTINCT ?pastClub; separator=", ") AS ?pastClubs)
        (GROUP_CONCAT(DISTINCT ?pastClubName; separator=", ") AS ?pastClubNames)
        (GROUP_CONCAT(DISTINCT ?pastClubLogo; separator=", ") AS ?pastClubLogos)
        ?born
    WHERE {{
        # Filter for a specific player by ID
        VALUES ?player_id {{ <http://football.org/ent/{player_id}> }} 
        
        ?player_id rdf:type fut-rel:Player .
        ?player_id fut-rel:name ?name .
        ?player_id fut-rel:position ?position .
        ?player_id fut-rel:nation ?nation_id .
        ?nation_id fut-rel:name ?nation .
        ?nation_id fut-rel:flag ?flag .
        ?player_id fut-rel:born ?born .
        
        # Get current club
        ?player_id fut-rel:club ?currentClub .
        FILTER NOT EXISTS {{ ?player_id fut-rel:left_club ?currentClub }}
        
        ?currentClub fut-rel:name ?currentClubName .
        ?currentClub fut-rel:logo ?currentClubLogo .
        ?currentClub fut-rel:color ?currentClubColor .
        ?currentClub fut-rel:alternateColor ?currentClubAltColor .

        # Get past clubs
        OPTIONAL {{
            ?player_id fut-rel:left_club ?pastClub .
            ?pastClub fut-rel:name ?pastClubName .
            ?pastClub fut-rel:logo ?pastClubLogo .
        }}
    }}
    GROUP BY ?player_id ?name ?nation ?flag ?currentClub ?currentClubName ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_player_results(results, player_id)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return get_default_player_data()

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
    
    # Convert abbreviated positions to full names
    positions = []
    for pos in raw_positions:
        if pos in position_mapping:
            positions.append(f"{position_mapping[pos]} ({pos})")
        else:
            positions.append(pos)
    
    # Extract past clubs
    past_clubs_str = result.get("pastClubs", {}).get("value", "")
    past_clubs_names_str = result.get("pastClubsNames", {}).get("value", "")
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
        "pos": positions,
        "country_name": result["nation"]["value"].split("/")[-1].replace("_", " ").title(),
        "flag": result["flag"]["value"],
        "teams": teams,
        "color": result["currentClubColor"]["value"],
        "alternate_color": result["currentClubAltColor"]["value"],
        "stats": query_player_stats(player_id)
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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?club_id
        ?abbreviation
        ?name
        ?stadium
        ?city
        ?league_id
        ?league_name
        ?flag
        ?logo
        ?color
        ?alternateColor
    WHERE {{
        VALUES ?club_id {{ <http://football.org/ent/{club_id}> }}
        
        ?club_id rdf:type fut-rel:Club .
        ?club_id fut-rel:name ?name .
        ?club_id fut-rel:abrv ?abbreviation .
        ?club_id fut-rel:stadium ?stadium .
        ?club_id fut-rel:city ?city .
        ?club_id fut-rel:league ?league_id .
        ?league_id fut-rel:name ?league_name .
        ?club_id fut-rel:country ?country .
        ?country fut-rel:flag ?flag .
        ?club_id fut-rel:logo ?logo .
        ?club_id fut-rel:color ?color .
        ?club_id fut-rel:alternateColor ?alternateColor .
    }}
    """

    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_club_results(results, club_id)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return get_default_club_data()

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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?player_id
        ?name
        ?born
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?nation
        ?flag
    WHERE {{
        VALUES ?club_id {{ <http://football.org/ent/{club_id}> }}
        
        ?player_id rdf:type fut-rel:Player .
        ?player_id fut-rel:name ?name .
        ?player_id fut-rel:position ?position .
        ?player_id fut-rel:nation ?nation_id .
        ?nation_id fut-rel:name ?nation .
        ?nation_id fut-rel:flag ?flag .
        ?player_id fut-rel:born ?born .
        ?player_id fut-rel:club ?club_id .
        FILTER NOT EXISTS {{ ?player_id fut-rel:left_club ?club_id }}
    }}
    GROUP BY ?player_id ?name ?born ?nation ?flag
    ORDER BY ?name
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_club_players_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?player_id
        ?name
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?nation
        ?flag
        (SAMPLE(?currentClubRaw) AS ?currentClub)
        (SAMPLE(?clubLogo) AS ?currentClubLogo)
        ?born
    WHERE { 
        ?player_id rdf:type fut-rel:Player .
        ?player_id fut-rel:name ?name .
        ?player_id fut-rel:position ?position .
        ?player_id fut-rel:nation ?nation_id .
        ?nation_id fut-rel:abrv ?nation .
        ?nation_id fut-rel:flag ?flag .
        ?player_id fut-rel:born ?born .
        
        # Choose the current club (one that has not been left)
        OPTIONAL {
            ?player_id fut-rel:club ?currentClubRaw .
            FILTER NOT EXISTS { ?player_id fut-rel:left_club ?currentClubRaw }
            
            OPTIONAL {
                ?currentClubRaw fut-rel:logo ?clubLogo .
            }
        }
    }
    GROUP BY ?player_id ?name ?nation ?flag ?born
    ORDER BY ?name
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_all_players_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
        
        if "currentClub" in player and player["currentClub"]["value"]:
            current_club = player["currentClub"]["value"].split("/")[-1]
            
        if "currentClubLogo" in player and player["currentClubLogo"]["value"]:
            current_club_logo = player["currentClubLogo"]["value"]
            
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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?club_id
        ?abbreviation
        ?name
        ?league
        ?flag
        ?logo
        ?color
        ?alternateColor
        (COUNT(?player) AS ?numPlayers)
    WHERE {
        ?club_id rdf:type fut-rel:Club .
        ?club_id fut-rel:name ?name .
        ?club_id fut-rel:abrv ?abbreviation .
        ?club_id fut-rel:league ?league_id .
        ?league_id fut-rel:name ?league .
        ?club_id fut-rel:country ?country .
        ?country fut-rel:flag ?flag .
        ?club_id fut-rel:logo ?logo .
        ?club_id fut-rel:color ?color .
        ?club_id fut-rel:alternateColor ?alternateColor .
        OPTIONAL {
            ?player fut-rel:club ?club_id .
            FILTER NOT EXISTS { ?player fut-rel:left_club ?club_id }
        }
    }
    GROUP BY ?club_id ?abbreviation ?league ?flag ?name ?logo ?color ?alternateColor
    ORDER BY ?name
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_all_clubs_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT ?stat_category ?stat_name ?stat_value
    WHERE {{
        VALUES ?player_id {{ <http://football.org/ent/{player_id}> }}

        ?player_id ?stat ?stat_value .
        ?stat fut-rel:type ?stat_cat_id .
        ?stat fut-rel:name ?stat_name .
        ?stat_cat_id fut-rel:name ?stat_category .
    }}
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_player_stats_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT ?stat_category ?stat_name ?stat_value
    WHERE {{
        VALUES ?club_id {{ <http://football.org/ent/{club_id}> }}
        
        ?club_id ?stat ?stat_value .
        ?stat fut-rel:type ?stat_cat_id .
        ?stat fut-rel:name ?stat_name .
        ?stat_cat_id fut-rel:name ?stat_category .
    }}
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_club_stats_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
