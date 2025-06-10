def get_club_id_query(club_name):

    if club_name == "Barcelona":
        type = "Q103229495"
        club_name = "FC Barcelona"
    else:
        type = "Q476028"

    if "Monchengladbach" in club_name:
        club_name = club_name.replace("Monchengladbach", "Mönchengladbach")
    elif club_name == "Atlético Madrid":
        club_name = "Atlético de Madrid"
    elif club_name == "Bayer Leverkusen":
        club_name = "Bayer 04 Leverkusen"
    elif club_name == "Celta Vigo":
        club_name = "Celta de Vigo"
    elif club_name == "TSG Hoffenheim":
        club_name = "TSG 1899 Hoffenheim"
    elif club_name == "AS Roma":
        club_name = "A.S. Roma"
    elif club_name == "Internazionale":
        club_name = "Inter Milan"
        

    """Returns SPARQL query for fetching club Wikidata ID."""
    return f"""
    SELECT DISTINCT 
        ?club 
    WHERE {{
        ?club wdt:P31 wd:{type}.
        ?club rdfs:label ?label .
        FILTER(LANG(?label) = "en")
        FILTER(CONTAINS(LCASE(?label), "{club_name.lower().replace('_', ' ')}"))

        ?club wdt:P118 ?league .
        FILTER(?league IN (wd:Q324867, wd:Q9448, wd:Q15804, wd:Q13394, wd:Q82595))
    }}
    """

def get_club_details_query(club_id):
    print(f"Fetching details for club ID: {club_id}")
    club_id = club_id.replace("http://www.wikidata.org/entity/", "")

    if club_id == 'Q12217':
        club_id = 'Q8682'

    """Returns SPARQL query for fetching club details by Wikidata ID."""
    return f"""
    SELECT
        (GROUP_CONCAT(DISTINCT ?sponsorInfo; separator=";") AS ?sponsors)
        ?kitInfo
        ?officialName 
        (GROUP_CONCAT(DISTINCT ?nickname; separator=";") AS ?nicknames) 
        ?audio
        ?inception
        ?presidentInfo
        ?coachInfo
        ?stadiumInfo
        (MAX(?followers) AS ?mediaFollowers)
    WHERE {{
        BIND(wd:{club_id} AS ?club)

        OPTIONAL {{ 
            ?club wdt:P859 ?sponsorEntity . 
            ?sponsorEntity rdfs:label ?sponsorName .
            FILTER(LANG(?sponsorName) = "en")
            
            OPTIONAL {{ ?sponsorEntity wdt:P2910 ?sponsorLogo . }}
            BIND(IF(BOUND(?sponsorLogo), 
                 CONCAT(?sponsorName, "|", STR(?sponsorLogo)), 
                 CONCAT(?sponsorName, "|", "")) AS ?sponsorInfo)
        }}
        OPTIONAL {{ 
            ?club wdt:P5995 ?kitEntity . 
            ?kitEntity rdfs:label ?kitName .
            FILTER(LANG(?kitName) = "en")
            OPTIONAL {{ ?kitEntity wdt:P8972 ?kitLogo . }}
            BIND(IF(BOUND(?kitLogo), 
                    CONCAT(?kitName, "|", STR(?kitLogo)), 
                    CONCAT(?kitName, "|", "")) AS ?kitInfo)
        }}
        OPTIONAL {{ ?club wdt:P1448 ?officialName . }}
        OPTIONAL {{ ?club wdt:P1449 ?nickname . }}
        OPTIONAL {{ ?club wdt:P443 ?audio . }}

        OPTIONAL {{ ?club wdt:P571 ?inception . }}
        OPTIONAL {{
            ?club wdt:P488 ?presidentEntity . 
            ?presidentEntity rdfs:label ?presidentName .
            FILTER(LANG(?presidentName) = "en")
            OPTIONAL {{ ?presidentEntity wdt:P18 ?presidentImage . }}
            BIND(IF(BOUND(?presidentImage), 
                 CONCAT(?presidentName, "|", STR(?presidentImage)), 
                 CONCAT(?presidentName, "|", "")) AS ?presidentInfo)
        }}
        OPTIONAL {{
            ?club wdt:P286 ?coachEntity . 
            ?coachEntity rdfs:label ?coachName .
            FILTER(LANG(?coachName) = "en")
            OPTIONAL {{ ?coachEntity wdt:P18 ?coachImage . }}
            BIND(IF(BOUND(?coachImage), 
                 CONCAT(?coachName, "|", STR(?coachImage)), 
                 CONCAT(?coachName, "|", "")) AS ?coachInfo)
        }}
        OPTIONAL {{
            ?club wdt:P115 ?stadiumEntity . 
            ?stadiumEntity rdfs:label ?stadiumName .
            FILTER(LANG(?stadiumName) = "en")
            BIND(CONCAT(STR(?stadiumEntity), "|", ?stadiumName) AS ?stadiumInfo)
        }}
        OPTIONAL {{
            ?club p:P8687 ?statement .
            ?statement ps:P8687 ?followers .
        }}
    }}
    GROUP BY ?kitInfo ?officialName ?audio ?inception ?presidentInfo ?coachInfo ?stadiumInfo
    """



def get_stadium_details_query(stadium_id):
    """Returns SPARQL query for fetching stadium details by Wikidata ID."""
    
    return f"""
    SELECT 
        ?label
        ?name
        ?opening
        ?image 
        ?location
        ?capacity
        ?categoryName
        (GROUP_CONCAT(DISTINCT ?eventName; separator=";") AS ?events) 
    WHERE {{
        BIND(wd:{stadium_id} AS ?stadium)        
        
        ?stadium rdfs:label ?label .
        FILTER(LANG(?label) = "en")

        OPTIONAL {{ ?stadium wdt:P1705 ?name . }}
        OPTIONAL {{ ?stadium wdt:P1619 ?opening . }}
        OPTIONAL {{ ?stadium wdt:P18 ?image . }}
        OPTIONAL {{ ?stadium wdt:P625 ?location . }}
        OPTIONAL {{ ?stadium wdt:P1083 ?capacity . }}
        OPTIONAL {{ 
            ?stadium wdt:P9803 ?categoryEntity . 
            ?categoryEntity rdfs:label ?categoryName .
            FILTER(LANG(?categoryName) = "en")
        }}
        OPTIONAL {{ 
            ?stadium wdt:P793 ?eventEntity . 
            ?eventEntity rdfs:label ?eventName .
            FILTER(LANG(?eventName) = "en")
        }}
    }}
    GROUP BY ?stadium ?label ?name ?opening ?image ?location ?capacity ?categoryName

    """