from repository.database import db_connection


def insert_new_player(player_name):
    with db_connection() as cursor:
        # Check if the player already exists
        check_if_player_exist = get_player_name_by_id(player_name)

        if check_if_player_exist is None:
            # Insert player if not already in the database
            cursor.execute('''
                INSERT INTO players (player_name) 
                VALUES (%s)
                ON CONFLICT (player_name) DO NOTHING
                RETURNING id;
            ''', (player_name,))

            result = cursor.fetchone()

            if result:
                new_id = result['id']
            else:
                new_id = None

            return new_id
        else:
            return check_if_player_exist


def get_player_name_by_id(player_name):
    with db_connection() as cursor:
        cursor.execute('SELECT id FROM players WHERE player_name = %s', (player_name,))
        result = cursor.fetchone()

        if result:
            player_id = result['id']
            return player_id
        else:
            return None
