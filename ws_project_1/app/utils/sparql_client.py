from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

# Configure your SPARQL endpoint
ENDPOINT_URL = "http://68f38762ffe4:7200/repositories/football"  # Replace with your actual endpoint URL

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
        ?currentClubLogo
        ?currentClubColor
        ?currentClubAltColor
        (GROUP_CONCAT(DISTINCT ?pastClub; separator=", ") AS ?pastClubs)
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
        ?currentClub fut-rel:logo ?currentClubLogo .
        ?currentClub fut-rel:color ?currentClubColor .
        ?currentClub fut-rel:alternateColor ?currentClubAltColor .

        # Get past clubs and their logos (if any)
        OPTIONAL {{
            ?player_id fut-rel:left_club ?pastClub .
            OPTIONAL {{ ?pastClub fut-rel:logo ?pastClubLogo . }}
        }}
    }}
    GROUP BY ?player_id ?name ?nation ?flag ?currentClub ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born
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
    
    # Extract positions from comma-separated string
    positions_str = result.get("positions", {}).get("value", "")
    positions = [pos.strip() for pos in positions_str.split(",")] if positions_str else []
    
    # Extract past clubs
    past_clubs_str = result.get("pastClubs", {}).get("value", "")
    past_clubs_logos_str = result.get("pastClubLogos", {}).get("value", "")
    
    past_clubs = past_clubs_str.split(", ") if past_clubs_str else []
    past_clubs_logos = past_clubs_logos_str.split(", ") if past_clubs_logos_str else []
    
    teams = []
    # Add current club
    teams.append({
        "id": result["currentClub"]["value"].split("/")[-1],
        "name": result["currentClub"]["value"].split("/")[-1].replace("_", " ").title(),
        "logo": result["currentClubLogo"]["value"],
    })
    
    # Add past clubs
    for i in range(len(past_clubs)):
        club_id = past_clubs[i].split("/")[-1]
        club_name = club_id.replace("_", " ").title()
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

# You can add more query functions here for team_detail, etc.
