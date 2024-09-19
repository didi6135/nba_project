from flask import Blueprint, request, jsonify

from service.player_season_service import main_calc




players_blueprint = Blueprint('players', __name__)

# 1. Get all answers
@players_blueprint.route('/players', methods=['GET'])
def get_players():
    position_options = ["PG", 'SG', 'SF', 'PF', 'C']
    position = request.args.get('position')
    season = request.args.get('season', type=int)

    if position not in position_options:
        return jsonify({"error": "Position is required"}), 400

    result = main_calc(position, season)
    return jsonify(result)