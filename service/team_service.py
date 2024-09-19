from toolz import pipe
from toolz.curried import partial

from models.teamPlayer import TeamPlayer
from repository.database import db_connection
from repository.player_repository import get_player_name_by_id
from repository.team_players_repository import find_team_player_by_id
from repository.team_repository import create_new_team, get_team_by_name, update_team


REQUIRED_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']


# Function to get all player names from the database in a single call
def get_all_player_names(player_ids):
    player_names = {}
    for player_id in player_ids:
        player_name = get_player_name_by_id(player_id)
        if player_name:
            player_names[player_id] = player_name
    return player_names




def get_last_season_position(player_id):
    with db_connection() as cursor:
        cursor.execute('''
            SELECT position 
            FROM player_seasons 
            WHERE player_id = %s 
            ORDER BY season DESC LIMIT 1;
        ''', (player_id,))
        result = cursor.fetchone()
        if result:
            return result['position']
        return None


def main_create_team(team_name, data):
    print(team_name)
    print(data)
    check_if_team_name_exist = get_team_by_name(team_name)
    if check_if_team_name_exist is not None:
        return None

    player_ids = data.keys()

    if len(player_ids) != len(REQUIRED_POSITIONS):
        raise ValueError("Exactly 5 players are required to create a team.")

    # Fetch all player names by player IDs
    player_names = get_all_player_names(player_ids)

    if len(player_names) != len(player_ids):
        raise ValueError("One or more players could not be found in the database.")

    # Map positions automatically
    team_players = []
    for i, player_id in enumerate(player_ids):
        player_name = player_names.get(player_id)
        if player_name:
            team_players.append(TeamPlayer(
                player_id=player_id,
                player_name=player_name,
                player_position=REQUIRED_POSITIONS[i]  # Assign position based on order
            ))

    # Validate that all required positions are covered
    positions_in_team = [player.player_position for player in team_players]
    missing_positions = [pos for pos in REQUIRED_POSITIONS if pos not in positions_in_team]

    if missing_positions:
        raise ValueError(f"Missing players for positions: {', '.join(missing_positions)}")

    # Insert the team into the database
    team_id = create_new_team(team_name, team_players)
    return team_id


# ------------------------------------------------------------
# ------------------ update team ----------------------
# ------------------------------------------------------------
def validate_team_players(players_with_positions, team_id):
    player_ids = list(players_with_positions.keys())
    check_players = pipe(
        player_ids,
        partial(map, find_team_player_by_id),
        list
    )

    existing_players = [
        player for player in check_players
        if player is not None and player['team_id'] != team_id
    ]

    if existing_players:
        formatted_existing_players = [
            f"{player['player_name']} (Player ID: {player['player_id']}, Team ID: {player['team_id']})"
            for player in existing_players
        ]
        return formatted_existing_players

    return None




def update_team_players(team_id, players_with_positions, name_team=None):
    update = update_team(players_with_positions, team_id, name_team)
    return update




# ------------------------------------------------------------
# ------------------ show team ----------------------
# ------------------------------------------------------------

def get_team_details(team_id):
    with db_connection() as cursor:
        cursor.execute('''
            SELECT team_name FROM teams WHERE id = %s;
        ''', (team_id,))
        team_result = cursor.fetchone()
        if not team_result:
            return None

        team_name = team_result['team_name']

        cursor.execute('''
            SELECT 
                p.player_name, tp.player_position, 
                SUM(ps.points) as total_points, 
                SUM(ps.games) as total_games,
                AVG(ps.two_percent) as avg_two_percent,
                AVG(ps.three_percent) as avg_three_percent,
                SUM(ps.assists) as total_assists,
                SUM(ps.turnovers) as total_turnovers
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            JOIN player_seasons ps ON p.id = ps.player_id
            WHERE tp.team_id = %s
            GROUP BY p.player_name, tp.player_position;
        ''', (team_id,))

        players = cursor.fetchall()
        return get_the_current_detail(players, team_name)




def get_the_current_detail(players, team_name):
    player_stats = []
    for player in players:
        atr = calculate_atr(player['total_assists'], player['total_turnovers'])
        ppg_ratio = calculate_ppg_ratio(player['total_points'], player['total_games'])

        player_stats.append({
            "playerName": player['player_name'],
            "position": player['player_position'],
            "points": player['total_points'],
            "games": player['total_games'],
            "twoPercent": player['avg_two_percent'],
            "threePercent": player['avg_three_percent'],
            "ATR": atr,
            "PPG Ratio": ppg_ratio
        })

    return {
        "team_name": team_name,
        "players": player_stats
    }

def calculate_atr(assists, turnovers):
    if turnovers == 0:
        return None
    return assists / turnovers


def calculate_ppg_ratio(points, games):
    if games == 0:
        return 0
    return points / games



# ------------------------------------------------------------
# ------------------ compare teams ----------------------
# ------------------------------------------------------------

def get_team_comparison_details(team_id):
    with db_connection() as cursor:
        cursor.execute('''
            SELECT 
                SUM(ps.points) as total_points, 
                AVG(ps.two_percent) as avg_two_percent,
                AVG(ps.three_percent) as avg_three_percent,
                SUM(ps.assists) as total_assists,
                SUM(ps.turnovers) as total_turnovers,
                SUM(ps.points) / SUM(ps.games) as avg_ppg_ratio
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            JOIN player_seasons ps ON p.id = ps.player_id
            WHERE tp.team_id = %s
        ''', (team_id,))

        result = cursor.fetchone()
        if result:
            atr = calculate_atr(result['total_assists'], result['total_turnovers'])
            return {
                "team_id": team_id,
                "points": result['total_points'],
                "twoPercent": result['avg_two_percent'],
                "threePercent": result['avg_three_percent'],
                "ATR": atr,
                "PPG Ratio": result['avg_ppg_ratio']
            }
        return None




def compare_teams(team_ids):
    teams = []

    for team_id in team_ids:
        team_details = get_team_comparison_details(team_id)
        if team_details:
            teams.append(team_details)

    sorted_teams = sorted(teams, key=lambda x: x['PPG Ratio'], reverse=True)

    return sorted_teams

# ------------------------------------------------------------
# ------------------ compare regular teams ----------------------
# ------------------------------------------------------------
def get_team_stats_by_name(team_name):
    with db_connection() as cursor:
        cursor.execute('''
                    SELECT 
                        SUM(ps.points) as total_points, 
                        AVG(ps.two_percent) as avg_two_percent,
                        AVG(ps.three_percent) as avg_three_percent,
                        SUM(ps.assists) as total_assists,
                        SUM(ps.turnovers) as total_turnovers,
                        SUM(ps.points) / SUM(ps.games) as avg_ppg_ratio
                    FROM player_seasons ps
                    WHERE ps.team = %s
                ''', (team_name,))

        result = cursor.fetchone()
        if result:
            # חישוב ATR עבור הקבוצה
            atr = calculate_atr(result['total_assists'], result['total_turnovers'])
            return {
                "team": team_name,
                "points": result['total_points'],
                "twoPercent": result['avg_two_percent'],
                "threePercent": result['avg_three_percent'],
                "ATR": atr,
                "PPG Ratio": result['avg_ppg_ratio']
            }
        return None


def compare_teams_by_name(team_names):
    teams = []

    for team_name in team_names:
        team_details = get_team_stats_by_name(team_name)
        if team_details:
            teams.append(team_details)

    sorted_teams = sorted(teams, key=lambda x: x['PPG Ratio'], reverse=True)

    return sorted_teams
