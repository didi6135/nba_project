import pytest
from flask import Flask, jsonify
from unittest.mock import patch

from controller.players_controller import players_blueprint

# Initialize a Flask app and register the blueprint for testing
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(players_blueprint)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Test case: position is missing or invalid
def test_get_players_invalid_position(client):
    response = client.get('/players', query_string={'position': 'invalid_position', 'season': 2024})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Position is required"}

# Test case: position is valid but season is missing (optional)
# @patch('service.player_season_service.main_calc')
# def test_get_players_valid_position_no_season(mock_main_calc, client):
#     # Mocking the main_calc function to return a sample result
#     mock_main_calc.return_value = [{"playerName": "LeBron James", "team": "Lakers", "points": 1000}]
#
#     response = client.get('/players', query_string={'position': 'PG'})
#     assert response.status_code == 200
#     result = response.get_json()
#     assert isinstance(result, list)
#     assert result[0]['playerName'] == "LeBron James"

# Test case: valid position and season provided
# @patch('service.player_season_service.main_calc')
# def test_get_players_valid_position_and_season(mock_main_calc, client):
#     # Mocking the main_calc function to return a sample result
#     mock_main_calc.return_value = [{"playerName": "Stephen Curry", "team": "Warriors", "points": 1200}]
#
#     response = client.get('/players', query_string={'position': 'PG', 'season': 2024})
#     assert response.status_code == 200
#     result = response.get_json()
#     assert isinstance(result, list)
#     assert result[0]['playerName'] == "Stephen Curry"
#     assert result[0]['points'] == 1200

# Test case: missing position query parameter
def test_get_players_missing_position(client):
    response = client.get('/players')
    assert response.status_code == 400
    assert response.get_json() == {"error": "Position is required"}
