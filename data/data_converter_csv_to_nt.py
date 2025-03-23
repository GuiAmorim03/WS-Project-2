import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.sparql import prepareQuery

df_main = pd.read_csv('players_data_light-2024_2025.csv')
df_colors_logos = pd.read_csv('teams.csv')
df_clubs_info = pd.read_csv('venues.csv')

players = set()
clubs = set()
leagues = set()
countries = set()

BASE_URL = 'http://football.org/'
ns_player = Namespace(BASE_URL + 'player/')
ns_club = Namespace(BASE_URL + 'club/')
ns_league = Namespace(BASE_URL + 'league/')
ns_country = Namespace(BASE_URL + 'country/')
ns_rel = Namespace(BASE_URL + 'rel/')

g = Graph()

def get_country_info(country_abrv):
    # pesquisar no df_colors_logos pelo country na coluna 'abbreviation'
    # country_name --> 'name'
    # country_flag --> 'logoURL'
    country_info = df_colors_logos[(df_colors_logos['abbreviation'] == country_abrv) & (~df_colors_logos['name'].str.contains(r'U(?:17|19|20|21|23)', na=False))]
    if (len(country_info) > 1):
        country_info = country_info[country_info['logoURL'].notna()]
    if (len(country_info) > 1):
        country_info = country_info[country_info['logoURL'].str.contains('countries')]
    country_name = country_info['name'].values[0]
    country_flag = country_info['logoURL'].values[0]

    if (country_abrv == 'GLP'): # este estava a dar erro, corrigi manualmente
        country_name = 'Guadalupe'
        country_flag = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Flag_of_Guadeloupe_%28local%29_variant.svg/220px-Flag_of_Guadeloupe_%28local%29_variant.svg.png'

    return country_name, country_flag

for index, row in df_main.iterrows():
    player = row['Player']
    club = row['Squad']
    league = row['Comp']
    country_abrv = row['Nation'].split(' ')[-1]

    # countries
    if country_abrv not in countries:
        countries.add(country_abrv)

        country_name, country_flag = get_country_info(country_abrv)
        
        country_uri = URIRef(ns_country + country_abrv)
        g.add((country_uri, ns_rel.name, Literal(country_name)))
        g.add((country_uri, ns_rel.flag, Literal(country_flag)))

    # leagues
    if league not in leagues:
        leagues.add(league)

        # verificar se o country da league já existe
        # se não existir, pesquisar no df_main 'Nation' por uma linha com o cod pequeno para obter o cod grande
        # pesquisar no df_colors_logos pelo country na coluna 'abbreviation', usando o cod grande
        # se ja existir, é só adicionar a liga
        # league_name --> 'Comp'
        # league_country --> cod grande
        league_id = league.split(' ')[0]
        league_name = ' '.join(league.split(' ')[1:])
        country_id = df_main[df_main['Nation'].str.contains(f'{league_id} ')]['Nation'].values[0].split(' ')[-1]
        if country_id not in countries:
            country_name, country_flag = get_country_info(country_id)
            country_uri = URIRef(ns_country + country_id)
            g.add((country_uri, ns_rel.name, Literal(country_name)))
            g.add((country_uri, ns_rel.flag, Literal(country_flag)))

        league_uri = URIRef(ns_league + league_id)
        g.add((league_uri, ns_rel.name, Literal(league_name)))
        g.add((league_uri, ns_rel.country, URIRef(ns_country + country_id)))

    # clubs
    if club not in clubs:
        clubs.add(club)
        if 'Utd' in club:
            club = club.replace('Utd', 'United')
        if 'Paris' in club:
            club = 'PSG'

        # pesquisar no df_colors_logos pelo club na coluna 'name'
        # club_id --> 'abbreviation'
        # club_name --> 'name'
        # club_color --> 'color'
        # club_alternate_color --> 'alternateColor'
        # club_logo --> 'logoURL'
        club_info = df_colors_logos[df_colors_logos['name'].str.contains(club, na=False)]
        if (len(club_info) == 0):
            club_info = df_colors_logos[df_colors_logos['name'].str.contains(club, na=False)]
        if (len(club_info) == 0):
            club_info = df_colors_logos[df_colors_logos['shortDisplayName'].str.contains(club, na=False)]
        if (len(club_info) == 0):
            club_name_parts = club.split(' ')
            for part in club_name_parts:
                club_info = df_colors_logos[df_colors_logos['name'].str.contains(part, na=False)]
                if (len(club_info) == 1):
                    break

        club_id = club_info['abbreviation'].values[0]
        club_name = club_info['name'].values[0]
        club_color = club_info['color'].values[0]
        club_alternate_color = club_info['alternateColor'].values[0]
        club_logo = club_info['logoURL'].values[0]

        num_to_search_location = club_info['venueId'].values[0] # usar este ID para pesquisar no df_clubs_info
        club_location = df_clubs_info[df_clubs_info['venueId'] == num_to_search_location]
        club_stadium = club_location['fullName'].values[0]
        club_city = club_location['city'].values[0]

        # ir buscar o country_id já existente
        league_id = league.split(' ')[0]
        league_uri = URIRef(ns_league + league_id)
        query = prepareQuery("""
            SELECT ?country
            WHERE {
                ?league ns_rel:country ?country .
            }
        """, initNs={'ns_rel': ns_rel})
        results = g.query(query, initBindings={'league': league_uri})
        row = next(iter(results), None)
        club_country_id = str(row.country)
    
        club_uri = URIRef(ns_club + club_id)
        g.add((club_uri, ns_rel.name, Literal(club_name)))
        g.add((club_uri, ns_rel.color, Literal(club_color)))
        g.add((club_uri, ns_rel.alternateColor, Literal(club_alternate_color)))
        g.add((club_uri, ns_rel.logo, Literal(club_logo)))
        g.add((club_uri, ns_rel.stadium, Literal(club_stadium)))
        g.add((club_uri, ns_rel.city, Literal(club_city)))
        g.add((club_uri, ns_rel.country, URIRef(club_country_id)))
        g.add((club_uri, ns_rel.league, URIRef(ns_league + league_id)))


g.serialize(destination="football_rdf_data.nt", format="nt", encoding="utf-8")
g.serialize(destination="football_rdf_data.n3", format="turtle", encoding="utf-8")
# print(df_main.head())