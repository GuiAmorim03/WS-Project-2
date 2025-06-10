from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

from .wikidata_queries import (
    get_club_id_query, get_club_details_query
)

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

def get_wikidata_client():
    """Returns a configured SPARQLWrapper instance for Wikidata."""
    sparql = SPARQLWrapper(WIKIDATA_ENDPOINT)
    sparql.setReturnFormat(JSON)
    return sparql

def process_query(query, process_func=None, additional_process_params=None, error_message=None, success_message=None):
    """
    Executes a SPARQL query on Wikidata and returns results.
    """
    sparql = get_wikidata_client()
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
            print(f"Wikidata SPARQL error: {e}")
        return None
    

def query_club_details_extra(club_name):
    """
    Queries Wikidata for additional details about a football club.

    First, it searches for the club Wikidata ID by name.
    If found, it retrieves extra club details

    Args:
        club_name: The original club name from our dataset
        
    Returns:
        list: List of processed extra club data ready for template rendering
    """

    club_id = process_query(get_club_id_query(club_name), process_func=process_club_id,
                         error_message="Error querying club wikidata id", success_message="Club wikidata id found")
    
    if not club_id:
        return []
    return process_query(get_club_details_query(club_id), process_func=process_club_details,
                                 error_message="Error querying club details", success_message="Club details found")
    

    

def process_club_id(id):
    """Process the WIKIDATA query results for club wikidata id into the format needed."""
    return id["results"]["bindings"][0]["club"]["value"]

def process_club_details(details):
    """Process the WIKIDATA query results for club details into the format needed."""
    if not details["results"]["bindings"]:
        return None
    
    result = details["results"]["bindings"][0]

    print(result)
    
    sponsors = [
        {
            "name": sponsor.split("|")[0],
            "logo": sponsor.split("|")[1]
        }
        for sponsor in result["sponsors"]["value"].split(";") 
        if sponsor and len(sponsor.split("|")) > 1 and len(sponsor.split("|")[1]) > 1
    ]

    brands = sponsors.copy()
    if "kitInfo" in result and result["kitInfo"]["value"]:
        brands.append(
            {
                "name": result["kitInfo"]["value"].split("|")[0],
                "logo": result["kitInfo"]["value"].split("|")[1] if len(result["kitInfo"]["value"].split("|")) > 1 else None
            }
        )

    president = None
    if "presidentInfo" in result and result["presidentInfo"]["value"]:
        president_parts = result["presidentInfo"]["value"].split("|")
        president = {
            "name": president_parts[0],
            "photo": president_parts[1] if len(president_parts) > 1 else None
        }

    coach = None
    if "coachInfo" in result and result["coachInfo"]["value"]:
        coach_parts = result["coachInfo"]["value"].split("|")
        coach = {
            "name": coach_parts[0],
            "photo": coach_parts[1] if len(coach_parts) > 1 else None
        }
    
    return {
        "brands": brands,
        "official_name": result["officialName"]["value"] if "officialName" in result else None,
        "nicknames": result["nicknames"]["value"].split(";") if "nicknames" in result else [],
        "audio": result["audio"]["value"] if "audio" in result else None,
        "inception": datetime.fromisoformat(result["inception"]["value"].replace("Z","")).strftime("%d %B %Y") if "inception" in result else None,
        "president": president,
        "coach": coach,
        "media_followers": int(result["mediaFollowers"]["value"]) if "mediaFollowers" in result else 0,
    }
