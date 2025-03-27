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
        (GROUP_CONCAT(DISTINCT ?pastClubName; separator=", ") AS ?pastClubsNames)
        (GROUP_CONCAT(DISTINCT ?pastClubLogo; separator=", ") AS ?pastClubLogos)
        ?born
    WHERE {{ 
        # Filter for a specific player by ID
        VALUES ?player_id {{ <http://football.org/ent/{player_id}> }} 
        
        ?player_id rdf:type fut-rel:Player .
        ?player_id fut-rel:name ?name .
        ?player_id fut-rel:position ?position .
        ?player_id fut-rel:nation ?nation .
        ?nation fut-rel:flag ?flag .
        ?player_id fut-rel:born ?born .
        
        # Identify the current club (one that has not been left)
        ?player_id fut-rel:club ?currentClub .
        FILTER NOT EXISTS {{ ?player_id fut-rel:left_club ?currentClub }}

        # The current club always has a logo and colors
        ?currentClub fut-rel:name ?currentClubName .
        ?currentClub fut-rel:logo ?currentClubLogo .
        ?currentClub fut-rel:color ?currentClubColor .
        ?currentClub fut-rel:alternateColor ?currentClubAltColor .

        # Get past clubs and their logos (if any)
        OPTIONAL {{
            ?player_id fut-rel:left_club ?pastClub .
            OPTIONAL {{ 
                        ?pastClub fut-rel:name ?pastClubName . 
                        ?pastClub fut-rel:logo ?pastClubLogo . 
                    }}
        }}
    }}
    GROUP BY ?player_id ?name ?nation ?flag ?currentClub ?currentClubName ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_player_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return get_default_player_data()

def process_player_results(results):
    """Process the SPARQL query results into the format needed for templates."""
    if not results["results"]["bindings"]:
        return get_default_player_data()
    
    result = results["results"]["bindings"][0]
    
    # Position mapping dictionary
    position_mapping = {
        "GK": "Goalkeeper",
        "CB": "Center Back",
        "LB": "Left Back",
        "RB": "Right Back",
        "DM": "Defensive Midfielder",
        "CM": "Center Midfielder",
        "MF": "Midfielder",
        "WM": "Wing Midfielder",
        "AM": "Attacking Midfielder",
        "WF": "Wing Forward",
        "FW": "Forward",
        "ST": "Striker",
        "CF": "Center Forward"
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
        "stats": []
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
        return process_club_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return get_default_club_data()

def process_club_results(results):
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
        "alternate_color": result["alternateColor"]["value"]
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
