from flask import Blueprint, request, jsonify

from repository.team_repository import get_team_by_id, delete_team
from service.team_service import main_create_team, validate_team_players, update_team_players, get_team_details

teams_blueprint = Blueprint('teams', __name__)


REQUIRED_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']

# 1. create team
@teams_blueprint.route('/teams', methods=['POST'])
def create_team():

    data = request.get_json()
    if 'name_team' not in data or 'players' not in data:
        return jsonify({"error": "Missing 'name_team' or 'players' in request body"}), 400


    name_team = data.get('name_team')
    players = data.get('players')
    print(data)

    if len(players) != 5:
        return jsonify({"error": "Team must have exactly 5 players"}), 400

    missing_positions = [position for position in REQUIRED_POSITIONS if position not in players.values()]
    if missing_positions:
        return jsonify({"error": f"Missing players for positions: {', '.join(missing_positions)}"}), 400

    try:
        team_id = main_create_team(name_team, data)
        if team_id:
            return jsonify({"message": "Team created successfully", "team_id": team_id}), 201
        elif team_id is None:
            return jsonify({'msg': 'This team name already exist pls choose another'})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": "An error occurred while creating the team"}), 500


@teams_blueprint.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    data = request.get_json()

    team = get_team_by_id(team_id)
    if not team:
        return jsonify({"error": f"Team with ID {team_id} does not exist"}), 404

    if 'players' not in data or len(data['players']) != 5:
        return jsonify({"error": "Team must have exactly 5 players"}), 400

    players_with_positions = data['players']
    missing_positions = [position for position in REQUIRED_POSITIONS if position not in players_with_positions.values()]
    if missing_positions:
        return jsonify({"error": f"Missing players for positions: {', '.join(missing_positions)}"}), 400

    existing_players = validate_team_players(players_with_positions, team_id)
    if existing_players:
        return jsonify({"error": f"Players already in other teams: {', '.join(map(str, existing_players))}"}), 400

    try:
        update_team_players(team_id, players_with_positions)
        return jsonify({"message": "Team updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while updating the team: {str(e)}"}), 500




@teams_blueprint.route('/teams/<int:team_id>', methods=['DELETE'])
def delete_team_endpoint(team_id):
    team = get_team_by_id(team_id)
    if not team:
        return jsonify({"error": f"Team with ID {team_id} does not exist"}), 404

    try:
        delete_team(team_id)
        return jsonify({"message": f"Team with ID {team_id} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while deleting the team: {str(e)}"}), 500



@teams_blueprint.route('/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    try:
        team_details = get_team_details(team_id)

        if not team_details:
            return jsonify({"error": f"Team with ID {team_id} does not exist"}), 404

        return jsonify(team_details), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while retrieving the team: {str(e)}"}), 500