from toolz import pipe
from toolz.curried import partial

from models.teamPlayer import TeamPlayer
from repository.database import db_connection
from repository.player_repository import get_player_name_by_id
from repository.team_players_repository import find_team_player_by_id
from repository.team_repository import create_new_team, get_team_by_name, update_team


# 1. find the players in the db
def get_all_player_name(player_ids):
    return pipe(
        player_ids,
        partial(map, get_player_name_by_id),
        list
    )



def main_create_team(team_name, data):

    check_if_team_name_exist = get_team_by_name(team_name)
    if check_if_team_name_exist is None:

        team_players = pipe(
            data['players'].items(),
            partial(map, lambda p: TeamPlayer(
                player_id=int(p[0]),
                player_name=get_player_name_by_id(int(p[0])),
                player_position=p[1]
            )),
            list
        )

        team_id = create_new_team(team_name, team_players)
        return team_id
    else:
        return None




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
        player_id for player_id in check_players
        if player_id is not None and player_id['team_id'] != team_id
    ]
    if existing_players:
        return existing_players
    return None



def update_team_players(team_id, players_with_positions):
    update = update_team(players_with_positions, team_id)
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



