from repository.database import db_connection


def find_team_player_by_id(player_id):
    with db_connection() as cursor:
        cursor.execute('''
            SELECT tp.team_id, tp.player_id, p.player_name 
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            WHERE tp.player_id = %s;
        ''', (player_id,))

        result = cursor.fetchone()
        if result:
            return result  # מחזיר גם את שם השחקן
    return None



def find_player_name_by_id(player_id):
    with db_connection() as cursor:
        cursor.execute('''
            SELECT player_name FROM players WHERE id = %s;
        ''', (player_id,))
        result = cursor.fetchone()
        if result:
            return result['player_name']
        return None
