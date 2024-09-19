import pytest
from flask import json

from main import create_app
from repository.team_repository import get_team_by_id, delete_team
from service.team_service import main_create_team


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def new_team():
    return {
    "name_team": "Lakers Test",
    "players": [3, 5, 1, 10, 4]
}


def test_create_team_success(client, new_team):
    """Test creating a new team"""
    response = client.post('/teams', json=new_team)
    assert response.status_code == 201
    data = response.get_json()
    assert "Team created successfully" in data['message']


def test_create_team_missing_fields(client):
    """Test creating a team with missing fields"""
    response = client.post('/teams', json={"name_team": "Team A"})
    assert response.status_code == 400
    assert "Missing 'name_team' or 'players' in request body" in response.get_json()['error']


def test_create_team_invalid_player_count(client):
    """Test creating a team with an invalid number of players"""
    response = client.post('/teams', json={
        "name_team": "Team A",
        "players": ["player1"]
    })
    assert response.status_code == 400
    assert "Team must have exactly 5 players" in response.get_json()['error']


def test_get_team_by_id(client, new_team):
    """Test fetching a team by ID"""
    # Create the team first
    response = client.post('/teams', json=new_team)
    team_id = response.get_json()['team_id']

    response = client.get(f'/teams/{team_id}')
    assert response.status_code == 200
    team_data = response.get_json()
    assert team_data['name_team'] == new_team['name_team']


def test_update_team(client, new_team):
    """Test updating an existing team"""
    # Create the team first
    response = client.post('/teams', json=new_team)
    team_id = response.get_json()['team_id']

    updated_data = {
        "name_team": "Team A Updated",
        "players": ["player6", "player7", "player8", "player9", "player10"]
    }

    response = client.put(f'/teams/{team_id}', json=updated_data)
    assert response.status_code == 200
    assert "Team updated successfully" in response.get_json()['message']


def test_delete_team(client, new_team):
    """Test deleting a team by ID"""
    # Create the team first
    response = client.post('/teams', json=new_team)
    team_id = response.get_json()['team_id']

    response = client.delete(f'/teams/{team_id}')
    assert response.status_code == 200
    assert f"Team with ID {team_id} deleted successfully" in response.get_json()['message']

    # Ensure team is actually deleted
    response = client.get(f'/teams/{team_id}')
    assert response.status_code == 404
    assert f"Team with ID {team_id} does not exist" in response.get_json()['error']
