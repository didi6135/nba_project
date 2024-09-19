import os

from flask import Flask

from controller.players_controller import players_blueprint
from controller.team_controller import teams_blueprint
from repository.database import create_tables, drop_all_tables

def create_app():
    app = Flask(__name__)

    app.register_blueprint(blueprint=players_blueprint, url_prefix='/api')
    app.register_blueprint(blueprint=teams_blueprint, url_prefix='/api')

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return app

if __name__ == '__main__':
    # create_tables()
    app = create_app()
    app.run(debug=True)
    # drop_all_tables()



