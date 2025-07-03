def get_city_details_query(city_name):
    print(f"Fetching details for city: {city_name}")


    """Returns SPARQL query for fetching coty details by city name"""
    return f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

    SELECT 
        ?name
        (COALESCE(?population, ?population2, ?population3) AS ?populationFinal)
        (COALESCE(?area, ?area2, ?area3) AS ?areaFinal)
        ?latitude
        ?longitude
        ?description
        ?image
    WHERE {{
        VALUES ?city {{ dbr:{city_name} }}

        ?city rdfs:label ?name .
        FILTER (lang(?name) = "en") .

        OPTIONAL {{ ?city dbo:populationUrban ?population . }}
        OPTIONAL {{ ?city dbo:populationTotal ?population2 . }}
        OPTIONAL {{ ?city dbp:urbanPop ?population3 . }}
        OPTIONAL {{ ?city dbo:areaUrban ?area . }}
        OPTIONAL {{ ?city dbo:areaTotal ?area2 . }}
        OPTIONAL {{ ?city dbo:area ?area3 . }}
        OPTIONAL {{ ?city geo:lat ?latitude . }}
        OPTIONAL {{ ?city geo:long ?longitude . }}
        OPTIONAL {{ ?city dbo:abstract ?description . FILTER (lang(?description) = "en") }}
        OPTIONAL {{ ?city dbo:thumbnail ?image . }}
    }}
    """

def get_event_details_query(event_name):
    print(f"Fetching details for event: {event_name}")

    """Returns SPARQL query for fetching event details by event name"""
    return f"""
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT  ?label ?abstract ?prev ?next
            (GROUP_CONCAT(DISTINCT ?hostCountry; separator=" & ") AS ?hostCountries)
            ?first ?second ?third ?pot ?ypot 
            (COALESCE(?goalkeeper, ?gk) AS ?got)
            (SAMPLE(?validTopScorer) AS ?topScorerOne) 
            ?image
    WHERE {{
        VALUES ?event {{ dbr:{event_name} }}

        ?event rdfs:label ?label .
        FILTER (lang(?label) = "en") .
        
        OPTIONAL {{ ?event dbo:abstract ?abstract . FILTER (lang(?abstract) = "en") }}
        OPTIONAL {{ ?event dbp:prevseason ?prev . }}
        OPTIONAL {{ ?event dbp:nextseason ?next . }}
        OPTIONAL {{ ?event dbp:country ?hostCountry . }}
        OPTIONAL {{ ?event dbp:champion ?first . }}
        OPTIONAL {{ ?event dbp:second ?second . }}
        OPTIONAL {{ ?event dbp:third ?third . }}
        OPTIONAL {{ ?event dbp:player ?pot . }}
        OPTIONAL {{ ?event dbp:youngPlayer ?ypot . }}
        OPTIONAL {{ ?event dbp:goalkeeper ?goalkeeper . }}
        OPTIONAL {{ ?event dbp:gk ?gk . }}
        OPTIONAL {{ ?event dbp:topScorer ?topScorer . }}
        OPTIONAL {{ ?event dbo:thumbnail ?image . }}
        OPTIONAL {{
            ?event dbp:topScorer ?topScorer .
            FILTER(STRLEN(STR(?topScorer)) > 0)
            BIND(?topScorer AS ?validTopScorer)
        }}
    }}
    GROUP BY ?event ?label ?abstract ?prev ?next ?first ?second ?third ?pot ?ypot ?goalkeeper ?gk ?image
    """

