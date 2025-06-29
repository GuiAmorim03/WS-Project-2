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


