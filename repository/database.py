from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictConnection, RealDictCursor
from config.sql_config import SQL_URI


def get_db_connection():
    return psycopg2.connect(SQL_URI, cursor_factory=RealDictCursor)


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Create the Players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        player_name VARCHAR(100) NOT NULL,
        UNIQUE(player_name)
    );
    ''')

    # Create the Player Seasons table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_seasons (
        id SERIAL PRIMARY KEY,
        player_id INT REFERENCES players(id) ON DELETE CASCADE,
        season INT NOT NULL,
        team VARCHAR(50) NOT NULL, 
        points INTEGER NOT NULL,
        games INTEGER NOT NULL,
        two_percent FLOAT,
        three_percent FLOAT,
        atr FLOAT,  
        ppg_ratio FLOAT,  
        UNIQUE(player_id, season) 
    );
    ''')

# -- Ensure each player has unique stats per season

    # Create the Teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id SERIAL PRIMARY KEY,
        team_name VARCHAR(100) NOT NULL UNIQUE
    );
    ''')

    # Create the Team-Player mapping (Many-to-Many relationship)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_players (
        team_id INT REFERENCES teams(id) ON DELETE CASCADE,
        player_id INT REFERENCES players(id) ON DELETE CASCADE,
        PRIMARY KEY (team_id, player_id)  -- Prevent duplicate player in the same team
    );
    ''')

    connection.commit()
    cursor.close()
    connection.close()





def drop_all_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Dropping tables in the correct order due to foreign key dependencies
    cursor.execute('''
        DROP TABLE IF EXISTS team_players;
        DROP TABLE IF EXISTS player_seasons;
        DROP TABLE IF EXISTS players;
        DROP TABLE IF EXISTS teams;  
    ''')

    connection.commit()
    cursor.close()
    connection.close()




@contextmanager
def db_connection():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()