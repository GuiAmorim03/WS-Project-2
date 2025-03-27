# SPARQL Queries
This document contains a list of SPARQL queries that can be used to query the data in the Knowledge Graph.

## Query 1: Get all the players in the dataset (player_id, name, positions, nation, flag, currentClub, currentClubLogo, born)
```sparql
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
```

## Query 2: Get a specific player's details (player_id, name, positions, nation, flag, currentClub, pastClubs, born)
```
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
WHERE { 
    # Filter for a specific player by ID
    VALUES ?player_id { <http://football.org/ent/aaron_ciammaglichella> } 
    
    ?player_id rdf:type fut-rel:Player .
    ?player_id fut-rel:name ?name .
    ?player_id fut-rel:position ?position .
    ?player_id fut-rel:nation ?nation_id .
    ?nation_id fut-rel:name ?nation .
    ?nation_id fut-rel:flag ?flag .
    ?player_id fut-rel:born ?born .
    
    # Get current club
    ?player_id fut-rel:club ?currentClub .
    FILTER NOT EXISTS { ?player_id fut-rel:left_club ?currentClub }
    
    ?currentClub fut-rel:name ?currentClubName .
    ?currentClub fut-rel:logo ?currentClubLogo .
    ?currentClub fut-rel:color ?currentClubColor .
    ?currentClub fut-rel:alternateColor ?currentClubAltColor .

    # Get past clubs
    OPTIONAL {
        ?player_id fut-rel:left_club ?pastClub .
        ?pastClub fut-rel:name ?pastClubName .
        ?pastClub fut-rel:logo ?pastClubLogo .
    }
}
GROUP BY ?player_id ?name ?nation ?flag ?currentClub ?currentClubName ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born
```

## Query 3: Get a specific player's stats (stat_category, stat_name, stat_value)
```
sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX fut-rel: <http://football.org/rel/>

SELECT ?stat_category ?stat_name ?stat_value
WHERE {
    VALUES ?player_id { <http://football.org/ent/aaron_ciammaglichella> } 

    ?player_id ?stat ?stat_value .
    ?stat fut-rel:type ?stat_cat_id .
    ?stat fut-rel:name ?stat_name .
    ?stat_cat_id fut-rel:name ?stat_category .
}
```

## Query 4: Get all the clubs in the dataset (club_id, abbreviation, name, league, flag, logo, color, alternateColor, numPlayers)
```
sparql
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
```

## Query 5: Get a specific club's details (club_id, abbreviation, name, stadium, city, league, flag, logo, color, alternateColor)
```
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
WHERE {
    VALUES ?club_id { <http://football.org/ent/heidenheim> }
    
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
}
```

## Query 6: Get all the club's players (player_id, name, born, positions, country, flag)
```
sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX fut-rel: <http://football.org/rel/>

SELECT
	?player_id
	?name
	?born
	(GROUP_CONCAT(DISTINCT ?position; separator=", ") AS ?positions)
	?nation
	?flag
WHERE {
	VALUES ?club_id { <http://football.org/ent/heidenheim> }
	
	?player_id rdf:type fut-rel:Player .
	?player_id fut-rel:name ?name .
	?player_id fut-rel:position ?position .
	?player_id fut-rel:nation ?nation_id .
    ?nation_id fut-rel:name ?nation .
	?nation_id fut-rel:flag ?flag .
	?player_id fut-rel:born ?born .
	?player_id fut-rel:club ?club_id .
	FILTER NOT EXISTS { ?player_id fut-rel:left_club ?club_id }
}
GROUP BY ?player_id ?name ?born ?nation ?flag
ORDER BY ?name
```