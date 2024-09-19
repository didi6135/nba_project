import pytest

from repository.database import create_tables, get_db_connection, drop_all_tables
from repository.player_repository import insert_new_player
from repository.team_repository import create_new_team, get_team_by_name, get_team_by_id, update_team, delete_team
from models.team import Team  # Adjust the import according to your project structure

@pytest.fixture(scope='module')
def setup_database():
    create_tables()  # Create necessary tables for tests
    yield
    conn = get_db_connection()
    cur = conn.cursor()
    drop_all_tables()  # Clean up after tests
    conn.commit()
    cur.close()
    conn.close()

def test_create_new_team(setup_database):
    """Test creating a new team"""
    player1_id = insert_new_player('Player One')
    player2_id = insert_new_player('Player Two')
    players_with_positions = {
        player1_id: 'PG',  # player_id as key
        player2_id: 'SG'   # position as value
    }

    team_id = create_new_team('Team A', players_with_positions)
    assert team_id is not None

    team = get_team_by_id(team_id)
    assert team['id'] == team_id

def test_get_team_by_name(setup_database):
    """Test fetching a team by name"""
    player1_id = insert_new_player('Player One')
    player2_id = insert_new_player('Player Two')
    players_with_positions = {
        player1_id: 'PG',
        player2_id: 'SG'
    }

    create_new_team('Team B', players_with_positions)
    team = get_team_by_name('Team B')
    assert team is not None
    assert team['id'] is not None

def test_get_nonexistent_team_by_name(setup_database):
    """Test fetching a nonexistent team by name"""
    team = get_team_by_name('Nonexistent Team')
    assert team is None

def test_update_team(setup_database):
    """Test updating an existing team"""
    player1_id = insert_new_player('Player One')
    player2_id = insert_new_player('Player Two')
    players_with_positions = {
        player1_id: 'PG',
        player2_id: 'SG'
    }

    team_id = create_new_team('Team C', players_with_positions)

    updated_players = {
        player1_id: 'SF',
        player2_id: 'PF'
    }

    update_team(updated_players, team_id, name_team='Updated Team C')

    team = get_team_by_id(team_id)
    assert team['id'] == team_id  # Team ID should remain the same
    # Additional checks to ensure players have been updated can be added here

def test_delete_team(setup_database):
    """Test deleting a team"""
    player1_id = insert_new_player('Player One')
    player2_id = insert_new_player('Player Two')
    players_with_positions = {
        player1_id: 'PG',
        player2_id: 'SG'
    }

    team_id = create_new_team('Team D', players_with_positions)

    delete_team(team_id)

    team = get_team_by_id(team_id)
    assert team is None  # Team should no longer exist
