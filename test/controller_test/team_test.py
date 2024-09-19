import pytest
from flask import json
from your_application import create_app  # Adjust to your app import
from repository.team_repository import get_team_by_id, delete_team
from service.team_service import main_create_team, get_last_season_position, update_team_players, validate_team_players

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mocker():
    from pytest_mock import mocker
    return mocker

@pytest.fixture
def mock_get_last_season_position(mocker):
    return mocker.patch('service.team_service.get_last_season_position', return_value='PG')

@pytest.fixture
def mock_main_create_team(mocker):
    return mocker.patch('service.team_service.main_create_team', return_value=1)

@pytest.fixture
def mock_get_team_by_id(mocker):
    return mocker.patch('repository.team_repository.get_team_by_id', return_value={'id': 1, 'name_team': 'Team A'})

@pytest.fixture
def mock_delete_team(mocker):
    return mocker.patch('repository.team_repository.delete_team')

@pytest.fixture
def mock_validate_team_players(mocker):
    return mocker.patch('service.team_service.validate_team_players', return_value=[])

def test_create_team_success(client, mock_get_last_season_position, mock_main_create_team):
    response = client.post('/teams', json={
        'name_team': 'Team A',
        'players': ['player1', 'player2', 'player3', 'player4', 'player5']
    })
    assert response.status_code == 201
    assert b'Team created successfully' in response.data

def test_create_team_missing_fields(client):
    response = client.post('/teams', json={'name_team': 'Team A'})
    assert response.status_code == 400
    assert b"Missing 'name_team' or 'players' in request body" in response.data

def test_create_team_invalid_player_count(client):
    response = client.post('/teams', json={'name_team': 'Team A', 'players': ['player1']})
    assert response.status_code == 400
    assert b"Team must have exactly 5 players" in response.data

def test_create_team_missing_positions(client, mock_get_last_season_position, mock_main_create_team):
    mock_get_last_season_position.side_effect = ['PG', 'SG', 'SF', 'PF', None]
    response = client.post('/teams', json={
        'name_team': 'Team A',
        'players': ['player1', 'player2', 'player3', 'player4', 'player5']
    })
    assert response.status_code == 400
    assert b"Missing players for positions: C" in response.data

def test_update_team_success(client, mock_get_team_by_id, mock_validate_team_players, mock_get_last_season_position):
    response = client.put('/teams/1', json={
        'name_team': 'Team A Updated',
        'players': ['player1', 'player2', 'player3', 'player4', 'player5']
    })
    assert response.status_code == 200
    assert b'Team updated successfully' in response.data

def test_update_team_not_found(client, mock_get_team_by_id):
    mock_get_team_by_id.return_value = None
    response = client.put('/teams/999', json={'players': ['player1', 'player2', 'player3', 'player4', 'player5']})
    assert response.status_code == 404
    assert b"Team with ID 999 does not exist" in response.data

def test_delete_team_success(client, mock_get_team_by_id, mock_delete_team):
    response = client.delete('/teams/1')
    assert response.status_code == 200
    assert b'Team with ID 1 deleted successfully' in response.data

def test_delete_team_not_found(client, mock_get_team_by_id):
    mock_get_team_by_id.return_value = None
    response = client.delete('/teams/999')
    assert response.status_code == 404
    assert b"Team with ID 999 does not exist" in response.data

def test_get_team_success(client, mock_get_team_by_id):
    response = client.get('/teams/1')
    assert response.status_code == 200
    assert b'Team A' in response.data

def test_get_team_not_found(client, mock_get_team_by_id):
    mock_get_team_by_id.return_value = None
    response = client.get('/teams/999')
    assert response.status_code == 404
    assert b"Team with ID 999 does not exist" in response.data

def test_compare_teams_success(client, mock_get_team_by_id):
    response = client.get('/teams/compare?team1=1&team2=2')
    assert response.status_code == 200
    assert b'comparison result' in response.data  # Adjust based on your actual response

def test_compare_teams_insufficient_teams(client):
    response = client.get('/teams/compare?team1=1')
    assert response.status_code == 400
    assert b"You must compare at least two teams." in response.data
