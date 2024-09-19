from flask import Blueprint, request, jsonify

average_ppg_by_position = {
    "PG": 20,
    "SG": 22,  # Shooting Guard average PPG
    "SF": 19,  # Small Forward
    "PF": 18,  # Power Forward
    "C": 17    # Center
}



players_blueprint = Blueprint('players', __name__)

# 1. Get all answers
@players_blueprint.route('/players', methods=['GET'])
def get_players():
    position = request.args.get('position')
    season = request.args.get('season', type=int)

    if not position:
        return jsonify({"error": "Position is required"}), 400