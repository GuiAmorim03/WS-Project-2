"""
SPIN rules client for executing and managing SPIN rule inferences.
"""

from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from .spin_queries import (
    get_all_spin_rules, get_clear_spin_inferences_query,
    get_enhanced_player_details_query, get_enhanced_all_players_query,
    get_teammates_query, get_compatriots_query, get_players_by_classification_query,
    get_club_rivals_query, get_enhanced_player_connection_query,
    get_efficiency_leaders_query
)

# Configure your SPARQL endpoint
ENDPOINT_URL = "http://graphdb:7200/repositories/football"

def get_sparql_update_client():
    """Returns a configured SPARQLWrapper instance for updates."""
    sparql = SPARQLWrapper(ENDPOINT_URL + "/statements")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)
    return sparql

def get_sparql_query_client():
    """Returns a configured SPARQLWrapper instance for queries."""
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setReturnFormat(JSON)
    return sparql

def execute_spin_rules():
    """
    Execute all SPIN rules to infer new knowledge.
    
    Returns:
        bool: True if all rules executed successfully, False otherwise
    """
    sparql = get_sparql_update_client()
    
    try:
        # Clear existing inferences first
        print("Clearing existing SPIN inferences...")
        sparql.setQuery(get_clear_spin_inferences_query())
        sparql.query()
        
        # Execute all SPIN rules
        rules = get_all_spin_rules()
        print(f"Executing {len(rules)} SPIN rules...")
        
        for i, rule in enumerate(rules, 1):
            print(f"Executing rule {i}/{len(rules)}...")
            sparql.setQuery(rule)
            sparql.query()
            
        print("All SPIN rules executed successfully.")
        return True
        
    except Exception as e:
        print(f"Error executing SPIN rules: {e}")
        return False

def clear_spin_inferences():
    """
    Clear all SPIN rule inferences from the knowledge base.
    
    Returns:
        bool: True if clearing was successful, False otherwise
    """
    sparql = get_sparql_update_client()
    
    try:
        print("Clearing SPIN rule inferences...")
        sparql.setQuery(get_clear_spin_inferences_query())
        sparql.query()
        print("SPIN rule inferences cleared successfully.")
        return True
        
    except Exception as e:
        print(f"Error clearing SPIN inferences: {e}")
        return False

def get_spin_rule_count():
    """
    Get the number of available SPIN rules.
    
    Returns:
        int: Number of SPIN rules
    """
    return len(get_all_spin_rules())

def execute_specific_spin_rule(rule_index):
    """
    Execute a specific SPIN rule by index.
    
    Args:
        rule_index (int): Index of the rule to execute (0-based)
        
    Returns:
        bool: True if rule executed successfully, False otherwise
    """
    sparql = get_sparql_update_client()
    rules = get_all_spin_rules()
    
    if 0 <= rule_index < len(rules):
        try:
            print(f"Executing SPIN rule {rule_index + 1}...")
            sparql.setQuery(rules[rule_index])
            sparql.query()
            print(f"SPIN rule {rule_index + 1} executed successfully.")
            return True
        except Exception as e:
            print(f"Error executing SPIN rule {rule_index + 1}: {e}")
            return False
    else:
        print(f"Invalid rule index: {rule_index}")
        return False

def query_enhanced_player_details(player_id):
    """
    Query enhanced player details including SPIN rule inferences.
    
    Args:
        player_id: The ID of the player to query
        
    Returns:
        dict: Enhanced player data with SPIN inferences
    """
    sparql = get_sparql_query_client()
    sparql.setQuery(get_enhanced_player_details_query(player_id))
    
    try:
        results = sparql.query().convert()
        return process_enhanced_player_results(results, player_id)
    except Exception as e:
        print(f"Error querying enhanced player details: {e}")
        return None

def process_enhanced_player_results(results, player_id):
    """Process enhanced player results including SPIN inferences."""
    if not results["results"]["bindings"]:
        return None
    
    result = results["results"]["bindings"][0]
    
    # Extract SPIN rule inferences
    spin_inferences = {}
    
    if result.get("currentAge"):
        spin_inferences["current_age"] = int(result["currentAge"]["value"])
    
    if result.get("efficiency"):
        spin_inferences["efficiency"] = round(float(result["efficiency"]["value"]), 3)
    
    if result.get("veteranStatus"):
        spin_inferences["is_veteran"] = result["veteranStatus"]["value"] == "true"
    
    if result.get("youngProspect"):
        spin_inferences["is_young_prospect"] = result["youngProspect"]["value"] == "true"
    
    if result.get("penaltySpecialist"):
        spin_inferences["is_penalty_specialist"] = result["penaltySpecialist"]["value"] == "true"
    
    if result.get("playmaker"):
        spin_inferences["is_playmaker"] = result["playmaker"]["value"] == "true"
    
    if result.get("goalThreat"):
        spin_inferences["is_goal_threat"] = result["goalThreat"]["value"] == "true"
    
    if result.get("disciplinaryRisk"):
        spin_inferences["is_disciplinary_risk"] = result["disciplinaryRisk"]["value"] == "true"
    
    if result.get("keyPlayer"):
        spin_inferences["is_key_player"] = result["keyPlayer"]["value"] == "true"
    
    if result.get("playerType"):
        spin_inferences["player_type"] = result["playerType"]["value"]
    
    if result.get("versatilePlayer"):
        spin_inferences["is_versatile"] = result["versatilePlayer"]["value"] == "true"
    
    return {
        "spin_inferences": spin_inferences,
        "base_data": result  # Include base data for compatibility
    }

def query_enhanced_all_players():
    """
    Query all players with SPIN rule inferences.
    
    Returns:
        list: List of enhanced player data
    """
    sparql = get_sparql_query_client()
    sparql.setQuery(get_enhanced_all_players_query())
    
    try:
        results = sparql.query().convert()
        return process_enhanced_all_players_results(results)
    except Exception as e:
        print(f"Error querying enhanced all players: {e}")
        return []

def process_enhanced_all_players_results(results):
    """Process enhanced all players results including SPIN inferences."""
    if not results["results"]["bindings"]:
        return []
    
    players = []
    for player in results["results"]["bindings"]:
        player_data = {
            "id": player["player_id"]["value"].split("/")[-1],
            "name": player["name"]["value"],
            "positions": [pos.strip() for pos in player.get("positions", {}).get("value", "").split(",") if pos.strip()],
            "nation": player["nation"]["value"],
            "flag": player["flag"]["value"],
            "born": int(player["born"]["value"]),
            "current_club": player.get("currentClubName", {}).get("value", ""),
            "club_logo": player.get("currentClubLogo", {}).get("value", ""),
            "spin_inferences": {}
        }
        
        # Add SPIN inferences
        if player.get("currentAge"):
            player_data["spin_inferences"]["current_age"] = int(player["currentAge"]["value"])
        
        if player.get("efficiency"):
            player_data["spin_inferences"]["efficiency"] = round(float(player["efficiency"]["value"]), 3)
        
        if player.get("playerType"):
            player_data["spin_inferences"]["player_type"] = player["playerType"]["value"]
        
        if player.get("veteranStatus"):
            player_data["spin_inferences"]["is_veteran"] = player["veteranStatus"]["value"] == "true"
        
        if player.get("youngProspect"):
            player_data["spin_inferences"]["is_young_prospect"] = player["youngProspect"]["value"] == "true"
        
        if player.get("keyPlayer"):
            player_data["spin_inferences"]["is_key_player"] = player["keyPlayer"]["value"] == "true"
        
        players.append(player_data)
    
    return players

def query_player_teammates(player_id):
    """Query a player's teammates using SPIN inferences."""
    sparql = get_sparql_query_client()
    sparql.setQuery(get_teammates_query(player_id))
    
    try:
        results = sparql.query().convert()
        return process_teammates_results(results)
    except Exception as e:
        print(f"Error querying player teammates: {e}")
        return []

def process_teammates_results(results):
    """Process teammates query results."""
    if not results["results"]["bindings"]:
        return []
    
    teammates = []
    for teammate in results["results"]["bindings"]:
        teammates.append({
            "id": teammate["teammate_id"]["value"].split("/")[-1],
            "name": teammate["name"]["value"],
            "photo_url": teammate["photo_url"]["value"],
            "positions": [pos.strip() for pos in teammate.get("positions", {}).get("value", "").split(",") if pos.strip()],
            "nation": teammate["nation"]["value"],
            "flag": teammate["flag"]["value"]
        })
    
    return teammates

def query_player_compatriots(player_id):
    """Query a player's compatriots using SPIN inferences."""
    sparql = get_sparql_query_client()
    sparql.setQuery(get_compatriots_query(player_id))
    
    try:
        results = sparql.query().convert()
        return process_compatriots_results(results)
    except Exception as e:
        print(f"Error querying player compatriots: {e}")
        return []

def process_compatriots_results(results):
    """Process compatriots query results."""
    if not results["results"]["bindings"]:
        return []
    
    compatriots = []
    for compatriot in results["results"]["bindings"]:
        compatriots.append({
            "id": compatriot["compatriot_id"]["value"].split("/")[-1],
            "name": compatriot["name"]["value"],
            "photo_url": compatriot["photo_url"]["value"],
            "positions": [pos.strip() for pos in compatriot.get("positions", {}).get("value", "").split(",") if pos.strip()],
            "current_club": compatriot.get("currentClubName", {}).get("value", ""),
            "club_logo": compatriot.get("currentClubLogo", {}).get("value", "")
        })
    
    return compatriots

def query_players_by_classification(classification):
    """
    Query players by SPIN rule classification.
    
    Args:
        classification: The classification to filter by (e.g., 'playmaker', 'goalThreat')
        
    Returns:
        list: List of players with the specified classification
    """
    sparql = get_sparql_query_client()
    sparql.setQuery(get_players_by_classification_query(classification))
    
    try:
        results = sparql.query().convert()
        return process_classification_results(results)
    except Exception as e:
        print(f"Error querying players by classification: {e}")
        return []

def process_classification_results(results):
    """Process players by classification query results."""
    if not results["results"]["bindings"]:
        return []
    
    players = []
    for player in results["results"]["bindings"]:
        player_data = {
            "id": player["player_id"]["value"].split("/")[-1],
            "name": player["name"]["value"],
            "photo_url": player["photo_url"]["value"],
            "positions": [pos.strip() for pos in player.get("positions", {}).get("value", "").split(",") if pos.strip()],
            "current_club": player.get("currentClubName", {}).get("value", ""),
            "club_logo": player.get("currentClubLogo", {}).get("value", ""),
            "nation": player["nation"]["value"],
            "flag": player["flag"]["value"]
        }
        
        if player.get("efficiency"):
            player_data["efficiency"] = round(float(player["efficiency"]["value"]), 3)
        
        players.append(player_data)
    
    return players

def query_club_rivals(club_id):
    """Query club rivals using SPIN inferences."""
    sparql = get_sparql_query_client()
    sparql.setQuery(get_club_rivals_query(club_id))
    
    try:
        results = sparql.query().convert()
        return process_rivals_results(results)
    except Exception as e:
        print(f"Error querying club rivals: {e}")
        return []

def process_rivals_results(results):
    """Process club rivals query results."""
    if not results["results"]["bindings"]:
        return []
    
    rivals = []
    for rival in results["results"]["bindings"]:
        rivals.append({
            "id": rival["rival_id"]["value"].split("/")[-1],
            "name": rival["name"]["value"],
            "logo": rival["logo"]["value"],
            "abbreviation": rival["abbreviation"]["value"],
            "stadium": rival["stadium"]["value"],
            "city": rival["city"]["value"],
            "league": rival["league_name"]["value"]
        })
    
    return rivals

def query_efficiency_leaders(limit=10):
    """Query top players by efficiency using SPIN inferences."""
    sparql = get_sparql_query_client()
    sparql.setQuery(get_efficiency_leaders_query(limit))
    
    try:
        results = sparql.query().convert()
        return process_efficiency_leaders_results(results)
    except Exception as e:
        print(f"Error querying efficiency leaders: {e}")
        return []

def process_efficiency_leaders_results(results):
    """Process efficiency leaders query results."""
    if not results["results"]["bindings"]:
        return []
    
    leaders = []
    for leader in results["results"]["bindings"]:
        leaders.append({
            "id": leader["player_id"]["value"].split("/")[-1],
            "name": leader["name"]["value"],
            "photo_url": leader["photo_url"]["value"],
            "efficiency": round(float(leader["efficiency"]["value"]), 3),
            "current_club": leader.get("currentClubName", {}).get("value", ""),
            "club_logo": leader.get("currentClubLogo", {}).get("value", ""),
            "nation": leader["nation"]["value"],
            "flag": leader["flag"]["value"]
        })
    
    return leaders

def check_enhanced_player_connection(player1_id, player2_id):
    """
    Check enhanced player connections using SPIN inferences.
    
    Args:
        player1_id: ID of the first player
        player2_id: ID of the second player
        
    Returns:
        dict: Enhanced connection details including SPIN inferences
    """
    sparql = get_sparql_query_client()
    
    connections = {}
    
    # Check SPIN rule connections
    spin_connections = ["teammate", "compatriot", "same_player_type", "past_teammate"]
    
    for connection_type in spin_connections:
        query = get_enhanced_player_connection_query(connection_type, player1_id, player2_id)
        sparql.setQuery(query)
        
        try:
            result = sparql.query().convert()
            connections[connection_type] = {
                "exists": result["boolean"],
                "description": f"Connected via SPIN rule: {connection_type.replace('_', ' ').title()}"
            }
        except Exception as e:
            print(f"Error checking {connection_type} connection: {e}")
            connections[connection_type] = {
                "exists": False,
                "description": f"Error checking {connection_type.replace('_', ' ').title()}"
            }
    
    # Summary of connections
    any_connection = any(conn["exists"] for conn in connections.values())
    
    return {
        "player1_id": player1_id,
        "player2_id": player2_id,
        "has_connection": any_connection,
        "spin_connections": connections
    }
