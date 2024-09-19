from models.team import Team
from repository.database import db_connection
from repository.team_players_repository import find_player_name_by_id


def create_new_team(team_name, players_with_positions):
    with db_connection() as cursor:

        cursor.execute('''
                INSERT INTO teams (team_name)
                VALUES (%s) RETURNING id
            ''', (team_name,))

        result = cursor.fetchone()
        if not result:
            raise ValueError("Failed to create team.")

        team_id = result['id']

        for player in players_with_positions:
            cursor.execute('''
                    INSERT INTO team_players (team_id, player_id, player_name, player_position)
                    VALUES (%s, %s, %s, %s)
                ''', (team_id, player.player_id, player.player_name, player.player_position))

        cursor.connection.commit()

    return team_id


def get_team_by_name(team_name):
    with db_connection() as cursor:
        cursor.execute('''
                    SELECT id FROM teams WHERE team_name = %s
                ''', (team_name,))

        result = cursor.fetchone()
        if result:
            return result
    return None


def get_team_by_id(team_id):
    with db_connection() as cursor:
        cursor.execute('''
                    SELECT id FROM teams WHERE id = %s
                ''', (team_id,))

        result = cursor.fetchone()
        if result:
            return result
    return None



def update_team(players_with_positions, team_id, name_team=None):
    try:
        with db_connection() as cursor:
            # If a new team name is provided, update the team's name
            if name_team:
                cursor.execute('''
                    UPDATE teams SET team_name = %s WHERE id = %s
                ''', (name_team, team_id))

            # First, delete the existing players in the team
            cursor.execute('''
                DELETE FROM team_players WHERE team_id = %s
            ''', (team_id,))

            # Insert the new players and their positions
            for player_id, position in players_with_positions.items():
                player_name = find_player_name_by_id(player_id)
                if player_name is None:
                    raise ValueError(f"Player with ID {player_id} not found")

                cursor.execute('''
                    INSERT INTO team_players (team_id, player_id, player_name, player_position)
                    VALUES (%s, %s, %s, %s)
                ''', (team_id, player_id, player_name, position))

            cursor.connection.commit()

    except Exception as e:
        cursor.connection.rollback()
        raise e



def delete_team(team_id):
    with db_connection() as cursor:
        cursor.execute('''
            DELETE FROM team_players WHERE team_id = %s
        ''', (team_id,))

        cursor.execute('''
            DELETE FROM teams WHERE id = %s
        ''', (team_id,))

        cursor.connection.commit()