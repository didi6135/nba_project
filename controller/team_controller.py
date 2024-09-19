from flask import Blueprint, request, jsonify

from repository.team_repository import get_team_by_id, delete_team
from service.team_service import main_create_team, validate_team_players, update_team_players, get_team_details, \
    compare_teams, get_team_stats_by_name, compare_teams_by_name, get_last_season_position

teams_blueprint = Blueprint('teams', __name__)


REQUIRED_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']

# 1. create team
@teams_blueprint.route('/teams', methods=['POST'])
def create_team():
    data = request.get_json()

    if 'name_team' not in data or 'players' not in data:
        return jsonify({"error": "Missing 'name_team' or 'players' in request body"}), 400

    name_team = data.get('name_team')
    players = data.get('players')  # List of player IDs

    if len(players) != 5:
        return jsonify({"error": "Team must have exactly 5 players"}), 400

    # Fetch players' positions from the last season
    player_positions = {}
    for player_id in players:
        last_season_position = get_last_season_position(player_id)
        if not last_season_position:
            return jsonify({"error": f"Player with ID {player_id} has no data for the last season"}), 400
        player_positions[player_id] = last_season_position

    # Check if all required positions are filled
    missing_positions = [position for position in REQUIRED_POSITIONS if position not in player_positions.values()]
    if missing_positions:
        return jsonify({"error": f"Missing players for positions: {', '.join(missing_positions)}"}), 400

    try:
        team_id = main_create_team(name_team, player_positions)
        if team_id:
            return jsonify({"message": "Team created successfully", "team_id": team_id}), 201
        elif team_id is None:
            return jsonify({'msg': 'This team name already exists, please choose another'}), 400

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": "An error occurred while creating the team"}), 500



@teams_blueprint.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    data = request.get_json()

    # Check if the team exists
    team = get_team_by_id(team_id)
    if not team:
        return jsonify({"error": f"Team with ID {team_id} does not exist"}), 404

    # Ensure 'players' is provided and contains exactly 5 players
    if 'players' not in data or len(data['players']) != 5:
        return jsonify({"error": "Team must have exactly 5 players"}), 400

    # Ensure 'name_team' is provided for updating the team name
    name_team = data.get('name_team', None)

    # Fetch players' positions from the last season for each player
    player_positions = {}
    for player_id in data['players']:
        last_season_position = get_last_season_position(player_id)
        if not last_season_position:
            return jsonify({"error": f"Player with ID {player_id} has no data for the last season"}), 400
        player_positions[player_id] = last_season_position

    # Check if all required positions are filled
    missing_positions = [position for position in REQUIRED_POSITIONS if position not in player_positions.values()]
    if missing_positions:
        return jsonify({"error": f"Missing players for positions: {', '.join(missing_positions)}"}), 400

    # Validate that no player belongs to another team
    existing_players = validate_team_players(player_positions, team_id)
    if existing_players:
        return jsonify({"error": f"Players already in other teams: {', '.join(map(str, existing_players))}"}), 400

    # Try to update the team
    try:
        update_team_players(team_id, player_positions, name_team)
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


@teams_blueprint.route('/teams/compare', methods=['GET'])
def compare_teams_endpoint():
    try:
        team_ids = [request.args.get(f"team{i}") for i in range(1, 100) if request.args.get(f"team{i}")]

        if len(team_ids) < 2:
            return jsonify({"error": "You must compare at least two teams."}), 400

        valid_team_ids = []
        for team_id in team_ids:
            if get_team_by_id(team_id):
                valid_team_ids.append(team_id)
            else:
                return jsonify({"error": f"Team with ID {team_id} does not exist."}), 404

        comparison_result = compare_teams(valid_team_ids)

        return jsonify(comparison_result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while comparing teams: {str(e)}"}), 500



@teams_blueprint.route('/teams/stats', methods=['GET'])
def compare_teams_stats():
    try:
        team_names = [request.args.get(f"team{i}") for i in range(1, 4) if request.args.get(f"team{i}")]

        if len(team_names) < 2:
            return jsonify({"error": "You must compare at least two teams."}), 400
        if len(team_names) > 3:
            return jsonify({"error": "You can compare up to 3 teams only."}), 400

        valid_team_names = []
        for team_name in team_names:
            team_stats = get_team_stats_by_name(team_name)
            if team_stats:
                valid_team_names.append(team_name)
            else:
                return jsonify({"error": f"Team '{team_name}' does not exist."}), 404

        comparison_result = compare_teams_by_name(valid_team_names)

        return jsonify(comparison_result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while comparing teams: {str(e)}"}), 500