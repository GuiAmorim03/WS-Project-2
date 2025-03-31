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
    ?currentClub
    ?currentClubLogo
    ?born
WHERE { 
    ?player_id rdf:type fut-rel:Player ;
               fut-rel:name ?name ;
               fut-rel:position ?position ;
               fut-rel:nation [ fut-rel:abrv ?nation ; fut-rel:flag ?flag ] ;
               fut-rel:born ?born ;
               fut-rel:club ?currentClub .

    OPTIONAL { ?currentClub fut-rel:logo ?currentClubLogo . }
}
GROUP BY ?player_id ?name ?nation ?flag ?born ?currentClub ?currentClubLogo
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
    VALUES ?player_id { <http://football.org/ent/marcus_rashford> } 

    ?player_id rdf:type fut-rel:Player ;
               fut-rel:name ?name ;
               fut-rel:position ?position ;
               fut-rel:nation [ fut-rel:name ?nation ; fut-rel:flag ?flag ] ;
               fut-rel:born ?born ;
               fut-rel:club ?currentClub .

    ?currentClub fut-rel:name ?currentClubName ;
                 fut-rel:logo ?currentClubLogo ;
                 fut-rel:color ?currentClubColor ;
                 fut-rel:alternateColor ?currentClubAltColor .

    # Get past clubs
    OPTIONAL {
        ?player_id fut-rel:past_club ?pastClub .
        ?pastClub fut-rel:name ?pastClubName ;
                  fut-rel:logo ?pastClubLogo .
    }
}
GROUP BY ?player_id ?name ?nation ?flag ?currentClub ?currentClubName 
         ?currentClubLogo ?currentClubColor ?currentClubAltColor ?born
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
    ?stat fut-rel:type/fut-rel:name ?stat_category ;
          fut-rel:name ?stat_name .
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
GROUP BY ?club_id ?abbreviation ?name ?league ?flag ?logo ?color ?alternateColor
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
    
    ?player_id rdf:type fut-rel:Player ;
               fut-rel:name ?name ;
               fut-rel:born ?born ;
               fut-rel:club ?club_id ;
               fut-rel:nation/fut-rel:name ?nation ;
               fut-rel:nation/fut-rel:flag ?flag ;
               fut-rel:position ?position .
}
GROUP BY ?player_id ?name ?born ?nation ?flag
ORDER BY ?name
```

## Query 7: Get the top 10 players in a specific stat (player_id, name, stat_name, stat_value)
```
sparql
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
WHERE {
    VALUES ?stat { <http://football.org/stat/min> } 

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

    OPTIONAL { ?player_id fut-rel:photo_url ?photo_url . }
}
ORDER BY DESC(xsd:float(?stat_value)) DESC(xsd:float(?min))
LIMIT 10
```

## Query 8: Get the top 10 clubs in a specific stat (club_id, name, stat_name, stat_value)
```
sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX fut-rel: <http://football.org/rel/>

SELECT
    ?club_id
    ?name
    ?stat_name
    ?stat_value
	?logo
WHERE {
    VALUES ?stat { <http://football.org/stat/crdr> } 
    
    ?club_id rdf:type fut-rel:Club ;
    		 fut-rel:name ?name ;
       		 fut-rel:logo ?logo ;
             ?stat ?stat_value .
    ?stat fut-rel:name ?stat_name .
}
ORDER BY DESC(?stat_value)
LIMIT 10
```

## Query 9: Get a specific club's stats (stat_category, stat_name, stat_value)
```
sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX fut-rel: <http://football.org/rel/>

SELECT ?stat_category ?stat_name ?stat_value
WHERE {
    VALUES ?club_id { <http://football.org/ent/heidenheim> }
    
    ?club_id ?stat ?stat_value .
    ?stat fut-rel:type [fut-rel:name ?stat_category];
          fut-rel:name ?stat_name .
}
```