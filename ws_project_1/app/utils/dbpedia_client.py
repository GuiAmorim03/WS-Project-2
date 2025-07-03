from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

from .dbpedia_queries import (
    get_city_details_query,
    get_event_details_query,
)

DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"

def get_dbpedia_client():
    """Returns a configured SPARQLWrapper instance for Dbpedia."""
    sparql = SPARQLWrapper(DBPEDIA_ENDPOINT)
    sparql.setReturnFormat(JSON)
    return sparql

def process_query(query, process_func=None, additional_process_params=None, error_message=None, success_message=None):
    """
    Executes a SPARQL query on Dbpedia and returns results.
    """
    sparql = get_dbpedia_client()
    sparql.setQuery(query)
    
    try:
        results = sparql.query().convert()
        if process_func:
            if additional_process_params:
                return process_func(results, **additional_process_params)
            return process_func(results)
        if success_message:
            print(success_message)
        return results
    except Exception as e:
        if error_message:
            print(f"{error_message}: {e}")
        else:
            print(f"Dbpedia SPARQL error: {e}")
        return None
    

def query_city_details(city_name):
    """
    Queries Dbpedia for city details by name.
    
    Args:
        city_name: The name of the city

    Returns:
        list: List of processed city data ready for template rendering
    """
    
    return process_query(get_city_details_query(city_name), process_func=process_city_details,
                            error_message="Error querying city details", success_message="City details found")
    

def process_city_details(details):
    """Process the DBpedia query results for city details into the format needed."""
    if not details["results"]["bindings"]:
        return []
    
    result = details["results"]["bindings"][0]
    print(result)

    return {
        "name": result.get("name", {}).get("value", ""),
        "population": result.get("populationFinal", {}).get("value", ""),
        "area": result.get("areaFinal", {}).get("value", ""),
        "latitude": result.get("latitude", {}).get("value", ""),
        "longitude": result.get("longitude", {}).get("value", ""),
        "description": result.get("description", {}).get("value", ""),
        "image": result.get("image", {}).get("value", "")
    }


def query_event_details(event_name):
    """
    Queries Dbpedia for event details by name.
    
    Args:
        event_name: The name of the event

    Returns:
        list: List of processed event data ready for template rendering
    """
    

    return process_query(get_event_details_query(event_name), process_func=process_event_details,
                            error_message="Error querying event details", success_message="Event details found")


def process_event_details(details):
    """Process the DBpedia query results for event details into the format needed."""
    if not details["results"]["bindings"]:
        return []
    
    result = details["results"]["bindings"][0]

    podium = []
    places = ["first", "second", "third"]
    for place in places:
        country = result.get(f"{place}", {}).get("value", "")
        if country:
            podium.append(country)

    actual_event = result.get("label", {}).get("value", "")

    if "FIFA" in actual_event:
        year = actual_event.split(" ")[0]
    else:
        year = actual_event.split(" ")[-1]
    year_prev = result.get("prev", {}).get("value", "")
    year_next = result.get("next", {}).get("value", "")
    if year_prev:
        event_prev = actual_event.replace(year, year_prev)
    else:
        event_prev = None
    if year_next:
        event_next = actual_event.replace(year, year_next)
    else:
        event_next = None
    
    return {
        "name": actual_event,
        "description": result.get("abstract", {}).get("value", ""),
        "hostCountries": result.get("hostCountries", {}).get("value", ""),
        "pot": result.get("pot", {}).get("value", ""),
        "ypot": result.get("ypot", {}).get("value", ""),
        "got": result.get("got", {}).get("value", ""),
        "topScorer": result.get("topScorerOne", {}).get("value", ""),
        "image": result.get("image", {}).get("value", ""),
        "podium": podium,
        "event_prev": {"name": event_prev, "url": event_prev.replace(" ", "_")} if event_prev else None,
        "event_next": {"name": event_next, "url": event_next.replace(" ", "_")} if event_next else None,
    }
