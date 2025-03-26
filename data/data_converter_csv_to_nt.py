import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF
from urllib.parse import quote
from unidecode import unidecode

df_main = pd.read_csv('players_data_light-2024_2025.csv')
df_colors_logos = pd.read_csv('teams.csv')
df_clubs_info = pd.read_csv('venues.csv')

players = set()
clubs = set()
leagues = set()
countries = set()

league_code_to_country_code = {}
club_name_to_club_id = {}

BASE_URL = 'http://football.org/'
ns_ent = Namespace(BASE_URL + 'ent/')
ns_rel = Namespace(BASE_URL + 'rel/')
ns_stat = Namespace(BASE_URL + 'stat/')
ns_stat_type = Namespace(BASE_URL + 'stat_type/')

g = Graph()

# Relações Estatisticas Tipo
g.add((ns_stat_type.playing_time, ns_rel.name, Literal('Playing Time')))
g.add((ns_stat_type.attacking, ns_rel.name, Literal('Attacking')))
g.add((ns_stat_type.defending, ns_rel.name, Literal('Defending')))
g.add((ns_stat_type.passing, ns_rel.name, Literal('Passing & Creativity')))
g.add((ns_stat_type.goalkeeping, ns_rel.name, Literal('Goalkeeping')))
g.add((ns_stat_type.miscellaneous, ns_rel.name, Literal('Miscellaneous')))

# Relações Estatisticas
def convert_stat_name_to_id(stat_name):
    return stat_name.lower().replace('%', '_pct').replace('+', '_plus_')

PLAYER = "player"
GK = "goalkeeper"
TEAM = "team"

stat_mappings = {
    "MP": {"description": "Matches Played", "type": ns_stat_type.playing_time, "entities": [PLAYER, GK]},
    "Starts": {"description": "Games Started", "type": ns_stat_type.playing_time, "entities": [PLAYER, GK]},
    "Min": {"description": "Minutes Played", "type": ns_stat_type.playing_time, "entities": [PLAYER, GK]},

    "Gls": {"description": "Goals", "type": ns_stat_type.attacking, "entities": [PLAYER, GK, TEAM]},
    "Ast": {"description": "Assists", "type": ns_stat_type.attacking, "entities": [PLAYER, GK]},
    "G+A": {"description": "Goals + Assists", "type": ns_stat_type.attacking, "entities": [PLAYER, GK]},
    "xG": {"description": "Expected Goals", "type": ns_stat_type.attacking, "entities": [PLAYER, GK, TEAM]},
    "xAG": {"description": "Expected Assists", "type": ns_stat_type.attacking, "entities": [PLAYER, GK]},
    "PK": {"description": "Penalties Scored", "type": ns_stat_type.attacking, "entities": [PLAYER, GK, TEAM]},
    "PKatt": {"description": "Penalties Attempted", "type": ns_stat_type.attacking, "entities": [PLAYER, GK, TEAM]},

    "Tkl": {"description": "Tackles", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},
    "TklW": {"description": "Tackles Won", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},
    "Blocks_stats_defense": {"description": "Blocks", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},
    "Int": {"description": "Interceptions", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},
    "Clr": {"description": "Clearances", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},
    "Err": {"description": "Errors Leading to Goal", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},
    "Recov": {"description": "Ball Recoveries", "type": ns_stat_type.defending, "entities": [PLAYER, TEAM]},

    "PrgP": {"description": "Progressive Passes", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "PrgC": {"description": "Progressive Carries", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "PrgR": {"description": "Progressive Runs", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "KP": {"description": "Key Passes", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "PPA": {"description": "Passes into Penalty Area", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "Live": {"description": "Total Passes", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "Cmp_stats_passing_types": {"description": "Passes Completed", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "Touches": {"description": "Touches", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "Mis": {"description": "Miscontrols", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},
    "Dis": {"description": "Times Dispossessed", "type": ns_stat_type.passing, "entities": [PLAYER, TEAM]},

    "GA": {"description": "Goals Conceded", "type": ns_stat_type.goalkeeping, "entities": [GK, TEAM]},
    "GA90": {"description": "Goals Conceded per 90 minutes", "type": ns_stat_type.goalkeeping, "entities": [GK, TEAM]},
    "Saves": {"description": "Saves", "type": ns_stat_type.goalkeeping, "entities": [GK, TEAM]},
    "Save%": {"description": "Save %", "type": ns_stat_type.goalkeeping, "entities": [GK]},
    "CS": {"description": "Clean Sheets", "type": ns_stat_type.goalkeeping, "entities": [GK, TEAM]},
    "CS%": {"description": "Clean Sheet %", "type": ns_stat_type.goalkeeping, "entities": [GK]},
    "PKA": {"description": "Penalties Faced", "type": ns_stat_type.goalkeeping, "entities": [GK, TEAM]},
    "PKsv": {"description": "Penalties Saved", "type": ns_stat_type.goalkeeping, "entities": [GK, TEAM]},

    "CrdY": {"description": "Yellow Cards", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK, TEAM]},
    "CrdR": {"description": "Red Cards", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK, TEAM]},
    "Fls": {"description": "Fouls Committed", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK, TEAM]},
    "PKcon": {"description": "Penalties Conceded", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK]},
    "PKwon": {"description": "Penalties Won", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK]},
    "OG": {"description": "Own Goals", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK, TEAM]},
    "Off_stats_misc": {"description": "Offsides", "type": ns_stat_type.miscellaneous, "entities": [PLAYER, GK, TEAM]}
}

for stat in stat_mappings:
    stat_id = convert_stat_name_to_id(stat)
    # print(stat)
    g.add((URIRef(ns_stat + stat_id), ns_rel.name, Literal(stat_mappings[stat]["description"])))
    g.add((URIRef(ns_stat + stat_id), ns_rel.type, URIRef(stat_mappings[stat]["type"])))

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

def convert_entity_name_to_id(entity_name):
    return quote(unidecode(entity_name.lower().replace(' ', '_')))

def check_player_exists(player_name):
    if player_name not in players:
        players.add(player_name)
        return False, convert_entity_name_to_id(player_name)
    else:
        # se o player já existe, é necessário verificar se é um falso duplicado
        # verificar se o 'Born' e 'Nation' são iguais
        repeated_player_info = df_main[df_main['Player'] == player_name]
        born_years = repeated_player_info['Born'].unique()
        nation = repeated_player_info['Nation'].unique()
        if len(born_years) > 1 or len(nation) > 1 or player_name == 'Vitinha':  # Há 2 Vitinha da mesma idade e país
            # são jogadores diferentes, precisa de id diferente
            return False, convert_entity_name_to_id(player_name)+"_2"
        else:
            return True, convert_entity_name_to_id(player_name)

def update_stat_on_graph(uri, stat, new_value, g):
    stat_id = convert_stat_name_to_id(stat)
    stat_predicate = URIRef(ns_stat + stat_id)

    if stat_id in ['pka', 'pksv', 'saves', 'ga', 'cs']: # por alguma razao estes estao a vir com casas decimais e deveriam ser int
        new_value = int(new_value)

    current_value = g.value(uri, stat_predicate)
    if (type(new_value)) == int or new_value is None:
        current_value = int(current_value if current_value is not None else 0)
    else:
        current_value = float(current_value if current_value is not None else 0)
    updated_value = current_value + new_value
    g.set((uri, stat_predicate, Literal(updated_value)))

for index, row in df_main.iterrows():
    club = row['Squad']
    league = row['Comp']
    country_abrv = row['Nation'].split(' ')[-1]

    # countries
    if country_abrv not in countries:
        countries.add(country_abrv)

        country_name, country_flag = get_country_info(country_abrv)
        
        country_uri = URIRef(ns_ent + country_abrv)
        g.add((country_uri, ns_rel.name, Literal(country_name)))
        g.add((country_uri, ns_rel.flag, Literal(country_flag)))
        g.add((country_uri, RDF.type, ns_rel.Country))

    # leagues
    if league not in leagues:
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
            country_uri = URIRef(ns_ent + country_id)
            g.add((country_uri, ns_rel.name, Literal(country_name)))
            g.add((country_uri, ns_rel.flag, Literal(country_flag)))
            g.add((country_uri, RDF.type, ns_rel.Country))

        league_uri = URIRef(ns_ent + league_id)
        g.add((league_uri, ns_rel.name, Literal(league_name)))
        g.add((league_uri, ns_rel.country, URIRef(ns_ent + country_id)))
        g.add((league_uri, RDF.type, ns_rel.League))

        leagues.add(league)
        league_code_to_country_code[league_id] = country_id

    # clubs
    if club not in clubs:
        club_original_name = club
        if 'Utd' in club:
            club = club.replace('Utd', 'United')
        if 'Paris' in club:
            club = 'PSG'
        if 'Wolves' in club:
            club = 'Wolverhampton'

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

        club_id = convert_entity_name_to_id(club_info['shortDisplayName'].values[0])
        club_abrv = club_info['abbreviation'].values[0]
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
        club_country_id = league_code_to_country_code[league_id]
    
        club_uri = URIRef(ns_ent + club_id)
        g.add((club_uri, ns_rel.name, Literal(club_name)))
        g.add((club_uri, ns_rel.abrv, Literal(club_abrv)))
        g.add((club_uri, ns_rel.color, Literal(club_color)))
        g.add((club_uri, ns_rel.alternateColor, Literal(club_alternate_color)))
        g.add((club_uri, ns_rel.logo, Literal(club_logo)))
        g.add((club_uri, ns_rel.stadium, Literal(club_stadium)))
        g.add((club_uri, ns_rel.city, Literal(club_city)))
        g.add((club_uri, ns_rel.country, URIRef(ns_ent + club_country_id)))
        g.add((club_uri, ns_rel.league, URIRef(ns_ent + league_id)))
        g.add((club_uri, RDF.type, ns_rel.Club))

        clubs.add(club_original_name)
        club_name_to_club_id[club_original_name] = club_id


    # players
        # player_id
        # player_name --> 'Player'
        # player_pos --> 'Pos'
        # player_year --> 'Born'
        # player_nation --> 'Nation' (country_abrv)
        # player_club --> 'Squad' (club_name_to_club_id)
    player_name = row['Player']
    player_exists, player_id = check_player_exists(player_name)
    player_uri = URIRef(ns_ent + player_id)
    player_pos = row['Pos'].split(',')
    player_club = club_name_to_club_id[row['Squad']]

    if not player_exists:
        try:
            player_year = int(row['Born'])
        except:
            player_year = 0
        player_nation = country_abrv

        g.add((player_uri, ns_rel.name, Literal(player_name)))
        for pos in player_pos:
            g.add((player_uri, ns_rel.position, Literal(pos)))
        g.add((player_uri, ns_rel.born, Literal(player_year)))
        g.add((player_uri, ns_rel.nation, URIRef(ns_ent + player_nation)))

    else:
        # indicar que já saiu do clube anterior
        club_registed = g.value(player_uri, ns_rel.club)
        matches_registed = int(g.value(player_uri, ns_stat.mp))
        matches_new = row['MP']
        if matches_new < matches_registed:
            first_club = URIRef(club_registed)
        else:
            first_club = URIRef(ns_ent + player_club)
        g.add((player_uri, ns_rel.left_club, first_club))

        # adicionar pos nova se necessário
        actual_pos = {str(pos) for pos in g.objects(player_uri, ns_rel.position)}
        new_pos = set(player_pos)
        diff_pos = new_pos.difference(actual_pos)
        for pos in diff_pos:
            g.add((player_uri, ns_rel.position, Literal(pos)))

    club_uri = URIRef(ns_ent + player_club)
    g.add((player_uri, ns_rel.club, club_uri))
    g.add((player_uri, RDF.type, ns_rel.Player))

    # stats
    main_pos = player_pos[0]
    for stat in stat_mappings:


        # player stats
        if (main_pos == "GK" and GK in stat_mappings[stat]["entities"] or main_pos != "GK" and PLAYER in stat_mappings[stat]["entities"]):
            stat_value = row[stat]
            if (pd.isna(stat_value)):
                if (stat == "Save%"):
                    stat_value = 0.0 # GK que estão com coluna vazia em vez de 0
                if (stat == "CS%"):
                    stat_value = row['CS'] / row['MP'] * 100
            update_stat_on_graph(player_uri, stat, stat_value, g)

            # team stats
            if (TEAM in stat_mappings[stat]["entities"]):
                update_stat_on_graph(club_uri, stat, stat_value, g)


g.serialize(destination="import/football_rdf_data.nt", format="nt", encoding="utf-8")
g.serialize(destination="import/football_rdf_data.n3", format="n3", encoding="utf-8")
# print(df_main.head())