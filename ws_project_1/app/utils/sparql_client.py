from SPARQLWrapper import SPARQLWrapper, JSON, POST
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
		?photo_url
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
        
        ?player_id rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:born ?born ;
                fut-rel:photo_url ?photo_url ;
                fut-rel:club ?currentClub .

        ?currentClub fut-rel:name ?currentClubName ;
                    fut-rel:logo ?currentClubLogo ;
                    fut-rel:color ?currentClubColor ;
                    fut-rel:alternateColor ?currentClubAltColor .

        # Get past clubs
        OPTIONAL {{
            ?player_id fut-rel:past_club ?pastClub .
            ?pastClub fut-rel:name ?pastClubName ;
                    fut-rel:logo ?pastClubLogo .
        }}
    }}
    GROUP BY ?player_id ?name ?nation ?flag ?photo_url ?currentClub ?currentClubName ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born
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
        
        ?club_id rdf:type fut-rel:Club ;
                fut-rel:name ?name ;
                fut-rel:abrv ?abbreviation ;
                fut-rel:stadium ?stadium ;
                fut-rel:city ?city ;
                fut-rel:league ?league_id ;
                fut-rel:logo ?logo ;
                fut-rel:color ?color ;
                fut-rel:alternateColor ?alternateColor ;
                fut-rel:country/fut-rel:flag ?flag .

        ?league_id fut-rel:name ?league_name .
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
		?photo_url
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?nation
        ?flag
    WHERE {{
        VALUES ?club_id {{ <http://football.org/ent/{club_id}> }}
        
        ?player_id rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                fut-rel:born ?born ;
                fut-rel:club ?club_id ;
                fut-rel:photo_url ?photo_url ;
                fut-rel:nation/fut-rel:name ?nation ;
                fut-rel:nation/fut-rel:flag ?flag ;
                fut-rel:position ?position .
    }}
    GROUP BY ?player_id ?name ?born ?photo_url ?nation ?flag
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
        ?currentClubName
        ?currentClubLogo
        ?born
    WHERE { 
        ?player_id rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:born ?born ;

        OPTIONAL { 
            ?player_id fut-rel:club ?currentClub .
            OPTIONAL { ?currentClub fut-rel:name ?currentClubName . }
            OPTIONAL { ?currentClub fut-rel:logo ?currentClubLogo . }
        }
    }
    GROUP BY ?player_id ?name ?nation ?flag ?born ?currentClubName ?currentClubLogo
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
        ?club_id rdf:type fut-rel:Club ;
                fut-rel:name ?name ;
                fut-rel:abrv ?abbreviation ;
                fut-rel:league/fut-rel:name ?league ;
                fut-rel:country/fut-rel:flag ?flag ;
                fut-rel:logo ?logo ;
                fut-rel:color ?color ;
                fut-rel:alternateColor ?alternateColor .
        
        OPTIONAL { ?player fut-rel:club ?club_id . }
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
        ?stat fut-rel:type/fut-rel:name ?stat_category ;
            fut-rel:name ?stat_name .
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
        ?stat fut-rel:type [fut-rel:name ?stat_category];
              fut-rel:name ?stat_name 
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
    sparql = get_sparql_client()
    
    if selected_node_id:
        # Query for a specific node and its adjacent nodes
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX fut-rel: <http://football.org/rel/>
        
        SELECT ?subject ?predicate ?object ?subjectLabel ?objectLabel ?subjectType ?objectType
        WHERE {{
            # Get relationships where selected node is the subject
            {{
                <{selected_node_id}> ?predicate ?object .
                BIND(<{selected_node_id}> AS ?subject)
                
                # Get labels and types
                OPTIONAL {{ ?subject rdfs:label ?subjectLabel }}
                OPTIONAL {{ ?object rdfs:label ?objectLabel }}
                OPTIONAL {{ ?subject rdf:type ?subjectType }}
                OPTIONAL {{ ?object rdf:type ?objectType }}
                
                # Filter out schema-related predicates
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema"))
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns"))
            }}
            UNION
            # Get relationships where selected node is the object
            {{
                ?subject ?predicate <{selected_node_id}> .
                BIND(<{selected_node_id}> AS ?object)
                
                # Get labels and types
                OPTIONAL {{ ?subject rdfs:label ?subjectLabel }}
                OPTIONAL {{ ?object rdfs:label ?objectLabel }}
                OPTIONAL {{ ?subject rdf:type ?subjectType }}
                OPTIONAL {{ ?object rdf:type ?objectType }}
                
                # Filter out schema-related predicates
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema"))
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns"))
            }}
        }}
        """
    else:
        # Query for the entire graph
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX fut-rel: <http://football.org/rel/>
        
        SELECT ?subject ?predicate ?object ?subjectLabel ?objectLabel ?subjectType ?objectType
        WHERE {
            ?subject ?predicate ?object .
            
            # Get human-readable labels where available
            OPTIONAL { ?subject rdfs:label ?subjectLabel }
            OPTIONAL { ?object rdfs:label ?objectLabel }
            
            # Get types
            OPTIONAL { ?subject rdf:type ?subjectType }
            OPTIONAL { ?object rdf:type ?objectType }
            
            # Filter out schema-related triples to focus on domain data
            FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema"))
            FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns"))
        }
        """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return {"nodes": [], "links": []}
    
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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query with dynamic stat and limit
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT
        ?player_id
        ?name
        ?photo_url
        ?stat_name
        ?stat_value
        ?club_name
        ?club_logo
        ?color
	    ?alternateColor
        ?flag
    WHERE {{
        VALUES ?stat {{ <http://football.org/stat/{stat_id}> }} 
        
        ?player_id rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                ?stat ?stat_value ;
                fut-rel:club ?club ;
                fut-rel:nation/fut-rel:flag ?flag ;
    		    fut-stat:min ?min .
        
        ?club fut-rel:name ?club_name ;
              fut-rel:logo ?club_logo ;
              fut-rel:color ?color ;
              fut-rel:alternateColor ?alternateColor .
        
        ?stat fut-rel:name ?stat_name .

        OPTIONAL {{ ?player_id fut-rel:photo_url ?photo_url . }}
    }}
    ORDER BY DESC(xsd:float(?stat_value)) DESC(xsd:float(?min))
    LIMIT {limit}
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_top_players_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
    sparql = get_sparql_client()
    
    # Construct the SPARQL query with dynamic stat and limit
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT
        ?club_id
        ?name
        ?stat_name
        ?stat_value
        ?logo
        ?flag
        ?league_name
        ?color
        ?alternateColor
    WHERE {{
        VALUES ?stat {{ <http://football.org/stat/{stat_id}> }} 
        
        ?club_id rdf:type fut-rel:Club ;
                fut-rel:name ?name ;
                ?stat ?stat_value ;
                fut-rel:logo ?logo ;
                fut-rel:color ?color ;
                fut-rel:alternateColor ?alternateColor ;
                fut-rel:country/fut-rel:flag ?flag ;
                fut-rel:league/fut-rel:name ?league_name .
        
        ?stat fut-rel:name ?stat_name .
    }}
    ORDER BY DESC(xsd:float(?stat_value)) ?club_id
    LIMIT {limit}
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_top_clubs_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []

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
        sparql = get_sparql_client()

        # Step 1: Retrieve current club
        query_get_club = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX fut-rel: <http://football.org/rel/>

        SELECT 
        ?currentClub
        WHERE {{
            <http://football.org/ent/{player_id}> fut-rel:club ?currentClub .
        }}
        """
        
        current_club = None
        try:
            sparql.setQuery(query_get_club)
            results = sparql.query().convert()

            print(results)
            
            result = results["results"]["bindings"][0]
            if result:
                current_club = result["currentClub"]["value"]
        except Exception as e:
            print("Error fetching current club:", e)

        return current_club

def update_player_club(player_id, current_club, club_id):

        sparql = SPARQLWrapper("http://graphdb:7200/repositories/football" + "/statements")
        sparql.setReturnFormat(JSON)

        current_club_id = current_club.split("/")[-1],
        current_club_id = current_club_id[0] 

        # Step 2: SPARQL Update - Move current club to pastClubs and update current club
        query_update = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX fut-rel: <http://football.org/rel/>

        DELETE {{
            <http://football.org/ent/{player_id}> fut-rel:club ?oldClub .
        }}
        INSERT {{
            <http://football.org/ent/{player_id}> fut-rel:club <http://football.org/ent/{club_id}> .
            {f'<http://football.org/ent/{player_id}> fut-rel:past_club <{current_club}> .' if current_club else ''}
        }}
        WHERE {{
            OPTIONAL {{ <http://football.org/ent/{player_id}> fut-rel:club ?oldClub . }}
        }}
        """

        try:
            sparql.setQuery(query_update)
            sparql.setMethod("POST")
            sparql.query()
        except Exception as e:
            print("Error updating player club:", e)

def query_all_nations():
    """
    Query and process a list of all nations from the SPARQL endpoint.
    
    Returns:
        list: List of all nations with name, flag, and ID"
        """
    
    sparql = get_sparql_client()
    
    # Construct the SPARQL query
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?abrv
        ?name
    WHERE {
        ?abrv rdf:type fut-rel:Country ;
                fut-rel:name ?name ;
    }
    ORDER BY ?name
    """
    
    # Execute the query
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return process_all_nations_results(results)
    except Exception as e:
        print(f"SPARQL query error: {e}")
        return []
    
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
        name: Player's name
        born: Year of birth
        positions: List of positions
        photo_url: URL of the player's photo
        nation: Nation URI
        club: Club ID
    """

    sparql = SPARQLWrapper(ENDPOINT_URL+"/statements")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)
    
    player_uri = f"http://football.org/ent/{id}"
    club_uri = f"http://football.org/ent/{club}"
    nation_uri = nation

    # Construct the SPARQL insert query
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        <{player_uri}> rdf:type fut-rel:Player ;
            fut-rel:name "{name}" ;
            fut-rel:born {born} ;
    """

    for position in positions:
        query += f'        fut-rel:position "{position}" ;\n'

    query += f"""        
            fut-rel:photo_url "{photo_url}" ;
            fut-rel:nation <{nation_uri}> ;
            fut-rel:club <{club_uri}> .
    }}
    """

    print(query)

    sparql.setQuery(query)

    try:
        sparql.query()
        print(f"Player {name} created successfully.")
    except Exception as e:
        print(f"Error creating player: {e}")
        return False
    return True
