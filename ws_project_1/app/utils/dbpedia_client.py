from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

from .dbpedia_queries import (
    get_city_details_query,
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


