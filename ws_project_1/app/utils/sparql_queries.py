def get_player_details_query(player_id):
    """Returns SPARQL query for fetching player details."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX ont: <http://football.org/ontology#>

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
        
        ?player_id rdf:type ?class ;
                fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:born ?born ;
                fut-rel:photo_url ?photo_url ;
                fut-rel:club ?currentClub .
        ?class rdfs:subClassOf* ont:Player .

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

def get_club_details_query(club_id):
    """Returns SPARQL query for fetching club details."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ont: <http://football.org/ontology#>
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
        
        ?club_id rdf:type ?class ;
                fut-rel:name ?name ;
                fut-rel:abrv ?abbreviation ;
                fut-rel:stadium ?stadium ;
                fut-rel:city ?city ;
                fut-rel:league ?league_id ;
                fut-rel:logo ?logo ;
                fut-rel:color ?color ;
                fut-rel:alternateColor ?alternateColor ;
                fut-rel:country/fut-rel:flag ?flag .
        ?class rdfs:subClassOf* ont:Club .

        ?league_id fut-rel:name ?league_name .
    }}
    """

def get_club_players_query(club_id):
    """Returns SPARQL query for fetching players of a specific club."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>

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
        
        ?player_id rdf:type ?class ;
                fut-rel:name ?name ;
                fut-rel:born ?born ;
                fut-rel:club ?club_id ;
                fut-rel:photo_url ?photo_url ;
                fut-rel:nation/fut-rel:name ?nation ;
                fut-rel:nation/fut-rel:flag ?flag ;
                fut-rel:position ?position .
        ?class rdfs:subClassOf* ont:Player .
    }}
    GROUP BY ?player_id ?name ?born ?photo_url ?nation ?flag
    ORDER BY ?name
    """

def get_all_players_query():
    """Returns SPARQL query for fetching all players."""
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>

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
        ?player_id rdf:type ?class ;
                fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:born ?born .
        ?class rdfs:subClassOf* ont:Player .

        OPTIONAL { 
            ?player_id fut-rel:club ?currentClub .
            OPTIONAL { ?currentClub fut-rel:name ?currentClubName . }
            OPTIONAL { ?currentClub fut-rel:logo ?currentClubLogo . }
        }
    }
    GROUP BY ?player_id ?name ?nation ?flag ?born ?currentClubName ?currentClubLogo
    ORDER BY ?name
    """

def get_all_clubs_query():
    """Returns SPARQL query for fetching all clubs."""
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>

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
        ?club_id rdf:type ?class ;
                fut-rel:name ?name ;
                fut-rel:abrv ?abbreviation ;
                fut-rel:league/fut-rel:name ?league ;
                fut-rel:country/fut-rel:flag ?flag ;
                fut-rel:logo ?logo ;
                fut-rel:color ?color ;
                fut-rel:alternateColor ?alternateColor .
        ?class rdfs:subClassOf* ont:Club .
        
        OPTIONAL { ?player fut-rel:club ?club_id . }
    }
    GROUP BY ?club_id ?abbreviation ?league ?flag ?name ?logo ?color ?alternateColor
    ORDER BY ?name
    """

def get_player_stats_query(player_id):
    """Returns SPARQL query for fetching player statistics."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?stat_category ?stat_name ?stat_value
    WHERE {{
        VALUES ?player_id {{ <http://football.org/ent/{player_id}> }}

        ?player_id ?stat ?stat_value .
        ?stat ont:statType/rdfs:label ?stat_category ;
            rdfs:label ?stat_name .
    }}
    """

def get_club_stats_query(club_id):
    """Returns SPARQL query for fetching club statistics."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>

    SELECT ?stat_category ?stat_name ?stat_value
    WHERE {{
        VALUES ?club_id {{ <http://football.org/ent/{club_id}> }}
        
        ?club_id ?stat ?stat_value .
        ?stat ont:statType/rdfs:label ?stat_category ;
            rdfs:label ?stat_name .
    }}
    """

def get_graph_data_query(selected_node_id=None):
    """Returns SPARQL query for fetching graph data, optionally filtered for a specific node."""
    if selected_node_id:
        return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX fut-rel: <http://football.org/rel/>
        
        SELECT ?subject ?predicate ?object ?subjectLabel ?objectLabel ?subjectType ?objectType
        WHERE {{
            # Get relationships where selected node is the subject
            {{
                <{selected_node_id}> ?predicate ?object .
                BIND(<{selected_node_id}> AS ?subject)
                
                # Get types
                OPTIONAL {{ ?subject rdf:type ?subjectType }}
                OPTIONAL {{ ?object rdf:type ?objectType }}
                
                # Filter out non-relevant predicates
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema"))
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns"))
                FILTER (!STRSTARTS(STR(?predicate), "http://football.org/stat"))
                FILTER (?predicate != <http://football.org/rel/photo_url>)
            }}
            UNION
            # Get relationships where selected node is the object
            {{
                ?subject ?predicate <{selected_node_id}> .
                BIND(<{selected_node_id}> AS ?object)
                
                # Get types
                OPTIONAL {{ ?subject rdf:type ?subjectType }}
                OPTIONAL {{ ?object rdf:type ?objectType }}
                
                # Filter out non-relevant predicates
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema"))
                FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns"))
                FILTER (!STRSTARTS(STR(?predicate), "http://football.org/stat"))
                FILTER (?predicate != <http://football.org/rel/photo_url>)
            }}
        }}
        """
    else:
        return """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX fut-rel: <http://football.org/rel/>

        SELECT ?subject ?predicate ?object ?subjectType ?objectType
        WHERE {
            ?subject ?predicate ?object .
            
            # Get types
            OPTIONAL { ?subject rdf:type ?subjectType }
            OPTIONAL { ?object rdf:type ?objectType }
            
            # Filter out unrelated triples
            FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema"))
            FILTER (!STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns"))
            FILTER (!STRSTARTS(STR(?predicate), "http://proton.semanticweb.org/protonsys"))
            FILTER (!STRSTARTS(STR(?predicate), "http://football.org/stat"))
            FILTER (!STRSTARTS(STR(?subject), "http://football.org/stat"))
            FILTER (?predicate != <http://football.org/rel/photo_url>)
            FILTER (?predicate != <http://www.w3.org/2002/07/owl#inverseOf>)
        }
        """

def get_top_players_by_stat_query(stat_id, limit=10):
    """Returns SPARQL query for fetching top players by a specific statistic."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>

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
        VALUES ?stat {{ <http://football.org/ontology#{stat_id}> }} 
        
        ?player_id rdf:type ?class ;
                fut-rel:name ?name ;
                ?stat ?stat_value ;
                fut-rel:club ?club ;
                fut-rel:nation/fut-rel:flag ?flag ;
                ont:min ?min .
        ?class rdfs:subClassOf* ont:Player .
        
        ?club fut-rel:name ?club_name ;
              fut-rel:logo ?club_logo ;
              fut-rel:color ?color ;
              fut-rel:alternateColor ?alternateColor .
        
        ?stat rdfs:label ?stat_name .

        OPTIONAL {{ ?player_id fut-rel:photo_url ?photo_url . }}
    }}
    ORDER BY DESC(xsd:float(?stat_value)) DESC(xsd:float(?min))
    LIMIT {limit}
    """

def get_top_clubs_by_stat_query(stat_id, limit=10):
    """Returns SPARQL query for fetching top clubs by a specific statistic."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ont: <http://football.org/ontology#>

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
        VALUES ?stat {{ <http://football.org/ontology#{stat_id}> }} 
        
        ?club_id rdf:type ?class ;
                fut-rel:name ?name ;
                ?stat ?stat_value ;
                fut-rel:logo ?logo ;
                fut-rel:color ?color ;
                fut-rel:alternateColor ?alternateColor ;
                fut-rel:country/fut-rel:flag ?flag ;
                fut-rel:league/fut-rel:name ?league_name .
        ?class rdfs:subClassOf* ont:Club .
        
        ?stat rdfs:label ?stat_name .
    }}
    ORDER BY DESC(xsd:float(?stat_value)) ?club_id
    LIMIT {limit}
    """

def get_player_club_query(player_id):
    """Returns SPARQL query for fetching a player's current club."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT 
    ?currentClub
    WHERE {{
        <http://football.org/ent/{player_id}> fut-rel:club ?currentClub .
    }}
    """

def get_update_player_club_query(player_id, current_club, club_id):
    """Returns SPARQL query for updating a player's club."""
    current_club_statement = f'<http://football.org/ent/{player_id}> fut-rel:past_club <{current_club}> .' if current_club else ''
    
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    DELETE {{
        <http://football.org/ent/{player_id}> fut-rel:club ?oldClub .
    }}
    INSERT {{
        <http://football.org/ent/{player_id}> fut-rel:club <http://football.org/ent/{club_id}> .
        {current_club_statement}
    }}
    WHERE {{
        OPTIONAL {{ <http://football.org/ent/{player_id}> fut-rel:club ?oldClub . }}
    }}
    """

def get_all_nations_query():
    """Returns SPARQL query for fetching all nations."""
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX ont: <http://football.org/ontology#>

    SELECT
        ?abrv
        ?name
    WHERE {
        ?abrv rdf:type ?class ;
                fut-rel:name ?name ;
        ?class rdfs:subClassOf* ont:Country .
    }
    ORDER BY ?name
    """

def get_create_player_query(player_uri, name, born, positions, photo_url, nation_uri, club_uri, stats_statements):
    """Returns SPARQL query for creating a new player."""
    positions_statements = ''.join([f'        fut-rel:position "{position}" ;\n' for position in positions])
    
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ont: <http://football.org/ontology#>

    INSERT DATA {{
        <{player_uri}> rdf:type ?class ;
            fut-rel:name "{name}" ;
            fut-rel:born {born} ;
{positions_statements}            
            fut-rel:photo_url "{photo_url}" ;
            fut-rel:nation <{nation_uri}> ;
            fut-rel:club <{club_uri}> ;
{stats_statements}
        ?class rdfs:subClassOf* ont:Player .
    }}
    """

def get_add_player_position_query(player_id, position):
    """Returns SPARQL query for adding a new position to a player."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    INSERT DATA {{
        <http://football.org/ent/{player_id}> fut-rel:position "{position}" .
    }}
    """

def get_player_connection_query(connection_type, player1_id, player2_id):
    """Returns SPARQL ASK query for checking connections between players."""
    if connection_type == "same_club":
        return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX fut-rel: <http://football.org/rel/>
        
        ASK {{
            {{
                # Both at same current club
                <http://football.org/ent/{player1_id}> fut-rel:club ?club .
                <http://football.org/ent/{player2_id}> fut-rel:club ?club .
            }} UNION {{
                # Player 1 current, Player 2 past
                <http://football.org/ent/{player1_id}> fut-rel:club ?club .
                <http://football.org/ent/{player2_id}> fut-rel:past_club ?club .
            }} UNION {{
                # Player 1 past, Player 2 current
                <http://football.org/ent/{player1_id}> fut-rel:past_club ?club .
                <http://football.org/ent/{player2_id}> fut-rel:club ?club .
            }} UNION {{
                # Both at same past club
                <http://football.org/ent/{player1_id}> fut-rel:past_club ?club .
                <http://football.org/ent/{player2_id}> fut-rel:past_club ?club .
            }}
        }}
        """
    elif connection_type == "same_country":
        return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX fut-rel: <http://football.org/rel/>
        
        ASK {{
            <http://football.org/ent/{player1_id}> fut-rel:nation ?country .
            <http://football.org/ent/{player2_id}> fut-rel:nation ?country .
        }}
        """
    elif connection_type == "same_position":
        return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX fut-rel: <http://football.org/rel/>
        
        ASK {{
            <http://football.org/ent/{player1_id}> fut-rel:position ?position .
            <http://football.org/ent/{player2_id}> fut-rel:position ?position .
        }}
        """
    return None

def get_delete_player_query(player_id):
    """Returns SPARQL query for deleting a player and all their connections."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    DELETE {{
        # Delete all properties where player is the subject
        <http://football.org/ent/{player_id}> ?p ?o .
        
        # Delete all properties where player is the object
        ?s ?p2 <http://football.org/ent/{player_id}> .
    }}
    WHERE {{
        # Get all statements where player is the subject
        <http://football.org/ent/{player_id}> ?p ?o .
        
        # Get all statements where player is the object
        OPTIONAL {{ ?s ?p2 <http://football.org/ent/{player_id}> . }}
    }}
    """
