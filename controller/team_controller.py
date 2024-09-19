from flask import Blueprint

teams_blueprint = Blueprint('teams', __name__)

# 1. Get all answers
@teams_blueprint.route('/answers', methods=['GET'])
def get_all():
    pass
