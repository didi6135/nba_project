from models.playerSeason import PlayerSeason
from repository.database import db_connection


def insert_player_season(player_season:PlayerSeason):
    with db_connection() as cursor:
        # Insert the player season or do nothing if a conflict occurs
        cursor.execute('''
            INSERT INTO player_seasons 
            (player_id, position, season, team, points, games, 
            two_percent, three_percent, atr, ppg_ratio, 
            assists, turnovers)
            
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (player_id, season) DO NOTHING
            RETURNING id;
        ''', (player_season.player_id, player_season.position, player_season.season, player_season.team,
              player_season.points, player_season.games, player_season.twoPercent,
              player_season.threePercent, player_season.ATR, player_season.PPG_ratio,
              player_season.assists, player_season.turnovers))

        # Fetch the newly inserted ID, if a row was inserted
        result = cursor.fetchone()

        if result is not None:
            new_id = result['id']
        else:
            new_id = None  # If no new row was inserted, return None

    return new_id


def get_player_by_position(position):
    with db_connection() as cursor:
        cursor.execute('''
            SELECT p.id, p.player_name, ps.team, ps.season, ps.points, ps.games, ps.two_percent, ps.three_percent, ps.assists, ps.turnovers
            FROM players p
            JOIN player_seasons ps ON p.id = ps.player_id
            WHERE ps.position = %s
        ''', (position,))

        players = cursor.fetchall()
    return players