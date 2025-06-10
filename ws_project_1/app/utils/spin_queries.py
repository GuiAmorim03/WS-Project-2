"""
SPIN rules queries for football ontology inference.
"""

def get_player_efficiency_rule():
    """Calculate Player Efficiency (Goals + Assists per 90 minutes)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:efficiency ?eff .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:gls ?goals .
        ?player fut-stat:ast ?assists .
        ?player fut-stat:min ?minutes .
        FILTER(?minutes > 0)
        BIND((?goals + ?assists) * 90.0 / ?minutes AS ?eff)
    }
    """

def get_teammates_rule():
    """Identify Teammates"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?player1 fut-rel:teammate ?player2 .
    }
    WHERE {
        ?player1 a fut-rel:Player .
        ?player2 a fut-rel:Player .
        ?player1 fut-rel:club ?club .
        ?player2 fut-rel:club ?club .
        FILTER(?player1 != ?player2)
    }
    """

def get_compatriots_rule():
    """Identify Compatriots (same nationality)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?player1 fut-rel:compatriot ?player2 .
    }
    WHERE {
        ?player1 a fut-rel:Player .
        ?player2 a fut-rel:Player .
        ?player1 fut-rel:nation ?country .
        ?player2 fut-rel:nation ?country .
        FILTER(?player1 != ?player2)
    }
    """

def get_current_age_rule():
    """Calculate Current Age"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?player fut-rel:currentAge ?age .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-rel:born ?birthYear .
        BIND(2025 - ?birthYear AS ?age)
    }
    """

def get_veterans_rule():
    """Identify Veterans (35+ years old)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?player fut-rel:veteranStatus true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-rel:born ?birthYear .
        FILTER(2025 - ?birthYear >= 35)
    }
    """

def get_young_prospects_rule():
    """Identify Young Prospects (under 23)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?player fut-rel:youngProspect true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-rel:born ?birthYear .
        FILTER(2025 - ?birthYear < 23)
    }
    """

def get_penalty_specialists_rule():
    """Identify Penalty Specialists (90%+ penalty success rate)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:penaltySpecialist true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:pk ?scored .
        ?player fut-stat:pkatt ?attempted .
        FILTER(?attempted > 0 && (?scored * 1.0 / ?attempted) >= 0.9)
    }
    """

def get_playmakers_rule():
    """Identify Playmakers (high assists and key passes relative to games)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:playmaker true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:ast ?assists .
        ?player fut-stat:kp ?keyPasses .
        ?player fut-stat:mp ?matches .
        FILTER(?matches > 0 && 
               (?assists * 1.0 / ?matches) >= 0.3 && 
               (?keyPasses * 1.0 / ?matches) >= 1.5)
    }
    """

def get_goal_threats_rule():
    """Identify Goal Threats (high goals per game)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:goalThreat true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:gls ?goals .
        ?player fut-stat:mp ?matches .
        FILTER(?matches > 0 && (?goals * 1.0 / ?matches) >= 0.5)
    }
    """

def get_disciplinary_risks_rule():
    """Identify Disciplinary Risks (high cards per game)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:disciplinaryRisk true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:crdy ?yellowCards .
        ?player fut-stat:crdr ?redCards .
        ?player fut-stat:mp ?matches .
        FILTER(?matches > 0 && 
               ((?yellowCards + ?redCards * 2) * 1.0 / ?matches) >= 0.3)
    }
    """

def get_key_players_rule():
    """Identify Key Players (play most minutes for their position)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:keyPlayer true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:min ?minutes .
        ?player fut-stat:mp ?matches .
        FILTER(?matches > 0 && (?minutes * 1.0 / ?matches) >= 70)
    }
    """

def get_striker_classification_rule():
    """Classify Strikers based on statistics"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:playerType "Striker" .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:gls ?goals .
        ?player fut-stat:mp ?matches .
        ?player fut-rel:position ?pos .
        FILTER(?matches > 0 && 
               (?goals * 1.0 / ?matches) >= 0.4 &&
               (CONTAINS(LCASE(?pos), "fw") || CONTAINS(LCASE(?pos), "forward")))
    }
    """

def get_defensive_midfielder_classification_rule():
    """Classify Defensive Midfielders based on statistics"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:playerType "Defensive Midfielder" .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:tkl ?tackles .
        ?player fut-stat:int ?interceptions .
        ?player fut-stat:mp ?matches .
        ?player fut-rel:position ?pos .
        FILTER(?matches > 0 && 
               ((?tackles + ?interceptions) * 1.0 / ?matches) >= 3.0 &&
               CONTAINS(LCASE(?pos), "mf"))
    }
    """

def get_versatile_players_rule():
    """Identify Versatile Players (good in multiple areas)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX fut-stat: <http://football.org/stat/>
    
    INSERT {
        ?player fut-rel:versatilePlayer true .
    }
    WHERE {
        ?player a fut-rel:Player .
        ?player fut-stat:gls ?goals .
        ?player fut-stat:ast ?assists .
        ?player fut-stat:tkl ?tackles .
        ?player fut-stat:mp ?matches .
        FILTER(?matches > 0 && 
               (?goals * 1.0 / ?matches) >= 0.1 &&
               (?assists * 1.0 / ?matches) >= 0.1 &&
               (?tackles * 1.0 / ?matches) >= 1.0)
    }
    """

def get_league_rivals_rule():
    """Infer club rivalries based on same league/city"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?club1 fut-rel:leagueRival ?club2 .
    }
    WHERE {
        ?club1 a fut-rel:Club .
        ?club2 a fut-rel:Club .
        ?club1 fut-rel:league ?league .
        ?club2 fut-rel:league ?league .
        ?club1 fut-rel:city ?city1 .
        ?club2 fut-rel:city ?city2 .
        FILTER(?club1 != ?club2 && ?city1 = ?city2)
    }
    """

def get_past_teammates_rule():
    """Infer past teammates (players who have played for the same club in the past)"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    INSERT {
        ?player1 fut-rel:pastTeammate ?player2 .
    }
    WHERE {
        ?player1 a fut-rel:Player .
        ?player2 a fut-rel:Player .
        ?player1 fut-rel:past_club ?club .
        ?player2 fut-rel:past_club ?club .
        FILTER(?player1 != ?player2)
    }
    """

def get_clear_spin_inferences_query():
    """Clear all SPIN rule inferences"""
    return """
    PREFIX fut-rel: <http://football.org/rel/>
    
    DELETE {
        ?s ?p ?o .
    }
    WHERE {
        ?s ?p ?o .
        FILTER(?p IN (
            fut-rel:efficiency, fut-rel:teammate, fut-rel:compatriot, 
            fut-rel:currentAge, fut-rel:veteranStatus, fut-rel:youngProspect,
            fut-rel:penaltySpecialist, fut-rel:playmaker, fut-rel:goalThreat,
            fut-rel:disciplinaryRisk, fut-rel:keyPlayer, fut-rel:playerType,
            fut-rel:versatilePlayer, fut-rel:leagueRival, fut-rel:pastTeammate
        ))
    }
    """

def get_all_spin_rules():
    """Get all SPIN rules in order"""
    return [
        get_player_efficiency_rule(),
        get_teammates_rule(),
        get_compatriots_rule(),
        get_current_age_rule(),
        get_veterans_rule(),
        get_young_prospects_rule(),
        get_penalty_specialists_rule(),
        get_playmakers_rule(),
        get_goal_threats_rule(),
        get_disciplinary_risks_rule(),
        get_key_players_rule(),
        get_striker_classification_rule(),
        get_defensive_midfielder_classification_rule(),
        get_versatile_players_rule(),
        get_league_rivals_rule(),
        get_past_teammates_rule()
    ]

def get_enhanced_player_details_query(player_id):
    """Returns enhanced SPARQL query for fetching player details with SPIN inferences."""
    return f"""
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
        ?currentAge
        ?efficiency
        ?veteranStatus
        ?youngProspect
        ?penaltySpecialist
        ?playmaker
        ?goalThreat
        ?disciplinaryRisk
        ?keyPlayer
        ?playerType
        ?versatilePlayer
    WHERE {{
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
        
        # SPIN rule inferences
        OPTIONAL {{ ?player_id fut-rel:currentAge ?currentAge . }}
        OPTIONAL {{ ?player_id fut-rel:efficiency ?efficiency . }}
        OPTIONAL {{ ?player_id fut-rel:veteranStatus ?veteranStatus . }}
        OPTIONAL {{ ?player_id fut-rel:youngProspect ?youngProspect . }}
        OPTIONAL {{ ?player_id fut-rel:penaltySpecialist ?penaltySpecialist . }}
        OPTIONAL {{ ?player_id fut-rel:playmaker ?playmaker . }}
        OPTIONAL {{ ?player_id fut-rel:goalThreat ?goalThreat . }}
        OPTIONAL {{ ?player_id fut-rel:disciplinaryRisk ?disciplinaryRisk . }}
        OPTIONAL {{ ?player_id fut-rel:keyPlayer ?keyPlayer . }}
        OPTIONAL {{ ?player_id fut-rel:playerType ?playerType . }}
        OPTIONAL {{ ?player_id fut-rel:versatilePlayer ?versatilePlayer . }}
    }}
    GROUP BY ?player_id ?name ?nation ?flag ?photo_url ?currentClub ?currentClubName ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born ?currentAge ?efficiency ?veteranStatus ?youngProspect ?penaltySpecialist ?playmaker ?goalThreat ?disciplinaryRisk ?keyPlayer ?playerType ?versatilePlayer
    """

def get_enhanced_all_players_query():
    """Returns enhanced SPARQL query for fetching all players with SPIN inferences."""
    return """
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
        ?currentAge
        ?efficiency
        ?playerType
        ?veteranStatus
        ?youngProspect
        ?keyPlayer
    WHERE { 
        ?player_id rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:born ?born .

        OPTIONAL { 
            ?player_id fut-rel:club ?currentClub .
            OPTIONAL { ?currentClub fut-rel:name ?currentClubName . }
            OPTIONAL { ?currentClub fut-rel:logo ?currentClubLogo . }
        }
        
        # SPIN rule inferences
        OPTIONAL { ?player_id fut-rel:currentAge ?currentAge . }
        OPTIONAL { ?player_id fut-rel:efficiency ?efficiency . }
        OPTIONAL { ?player_id fut-rel:playerType ?playerType . }
        OPTIONAL { ?player_id fut-rel:veteranStatus ?veteranStatus . }
        OPTIONAL { ?player_id fut-rel:youngProspect ?youngProspect . }
        OPTIONAL { ?player_id fut-rel:keyPlayer ?keyPlayer . }
    }
    GROUP BY ?player_id ?name ?nation ?flag ?born ?currentClubName ?currentClubLogo ?currentAge ?efficiency ?playerType ?veteranStatus ?youngProspect ?keyPlayer
    ORDER BY ?name
    """

def get_teammates_query(player_id):
    """Returns SPARQL query for fetching a player's teammates using SPIN inferences."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?teammate_id
        ?name
        ?photo_url
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?nation
        ?flag
    WHERE {{
        <http://football.org/ent/{player_id}> fut-rel:teammate ?teammate_id .
        
        ?teammate_id fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:photo_url ?photo_url .
    }}
    GROUP BY ?teammate_id ?name ?photo_url ?nation ?flag
    ORDER BY ?name
    """

def get_compatriots_query(player_id):
    """Returns SPARQL query for fetching a player's compatriots using SPIN inferences."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?compatriot_id
        ?name
        ?photo_url
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?currentClubName
        ?currentClubLogo
    WHERE {{
        <http://football.org/ent/{player_id}> fut-rel:compatriot ?compatriot_id .
        
        ?compatriot_id fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:photo_url ?photo_url .
                
        OPTIONAL {{ 
            ?compatriot_id fut-rel:club ?currentClub .
            ?currentClub fut-rel:name ?currentClubName ;
                        fut-rel:logo ?currentClubLogo .
        }}
    }}
    GROUP BY ?compatriot_id ?name ?photo_url ?currentClubName ?currentClubLogo
    ORDER BY ?name
    """

def get_players_by_classification_query(classification):
    """Returns SPARQL query for fetching players by SPIN rule classification."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?player_id
        ?name
        ?photo_url
        (GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
        ?currentClubName
        ?currentClubLogo
        ?nation
        ?flag
        ?efficiency
    WHERE {{
        ?player_id fut-rel:{classification} true ;
                rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                fut-rel:position ?position ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:photo_url ?photo_url .

        OPTIONAL {{ 
            ?player_id fut-rel:club ?currentClub .
            ?currentClub fut-rel:name ?currentClubName ;
                        fut-rel:logo ?currentClubLogo .
        }}
        
        OPTIONAL {{ ?player_id fut-rel:efficiency ?efficiency . }}
    }}
    GROUP BY ?player_id ?name ?photo_url ?currentClubName ?currentClubLogo ?nation ?flag ?efficiency
    ORDER BY DESC(?efficiency) ?name
    """

def get_club_rivals_query(club_id):
    """Returns SPARQL query for fetching club rivals using SPIN inferences."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>

    SELECT
        ?rival_id
        ?name
        ?logo
        ?abbreviation
        ?stadium
        ?city
        ?league_name
    WHERE {{
        <http://football.org/ent/{club_id}> fut-rel:leagueRival ?rival_id .
        
        ?rival_id fut-rel:name ?name ;
                fut-rel:logo ?logo ;
                fut-rel:abrv ?abbreviation ;
                fut-rel:stadium ?stadium ;
                fut-rel:city ?city ;
                fut-rel:league/fut-rel:name ?league_name .
    }}
    ORDER BY ?name
    """

def get_enhanced_player_connection_query(connection_type, player1_id, player2_id):
    """Returns enhanced SPARQL ASK query for checking connections including SPIN inferences."""
    base_query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    
    ASK {{
    """
    
    if connection_type == "teammate":
        base_query += f"""
        <http://football.org/ent/{player1_id}> fut-rel:teammate <http://football.org/ent/{player2_id}> .
        """
    elif connection_type == "compatriot":
        base_query += f"""
        <http://football.org/ent/{player1_id}> fut-rel:compatriot <http://football.org/ent/{player2_id}> .
        """
    elif connection_type == "same_player_type":
        base_query += f"""
        <http://football.org/ent/{player1_id}> fut-rel:playerType ?type .
        <http://football.org/ent/{player2_id}> fut-rel:playerType ?type .
        """
    elif connection_type == "past_teammate":
        base_query += f"""
        <http://football.org/ent/{player1_id}> fut-rel:pastTeammate <http://football.org/ent/{player2_id}> .
        """
    
    base_query += """
    }}
    """
    
    return base_query

def get_efficiency_leaders_query(limit=10):
    """Returns SPARQL query for fetching players with highest efficiency using SPIN inferences."""
    return f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX fut-rel: <http://football.org/rel/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT
        ?player_id
        ?name
        ?photo_url
        ?efficiency
        ?currentClubName
        ?currentClubLogo
        ?nation
        ?flag
    WHERE {{
        ?player_id rdf:type fut-rel:Player ;
                fut-rel:name ?name ;
                fut-rel:efficiency ?efficiency ;
                fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
                fut-rel:photo_url ?photo_url .

        OPTIONAL {{ 
            ?player_id fut-rel:club ?currentClub .
            ?currentClub fut-rel:name ?currentClubName ;
                        fut-rel:logo ?currentClubLogo .
        }}
        
        FILTER(?efficiency > 0)
    }}
    ORDER BY DESC(xsd:float(?efficiency))
    LIMIT {limit}
    """
