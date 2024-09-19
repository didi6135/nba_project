import os

from flask import Flask

from controller.players_controller import players_blueprint
from controller.team_controller import teams_blueprint
from repository.database import create_tables, drop_all_tables


def initialize_data():
    pass

def create_app():
    app = Flask(__name__)

    app.register_blueprint(blueprint=players_blueprint, url_prefix='/api')
    app.register_blueprint(blueprint=teams_blueprint, url_prefix='/api')


    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        initialize_data()
        print('---------------------- All data is set ---------------------- ')
        main()

    return app


def main():
    pass
    # user_id = register_user()
    # correct_count, total_time_taken, total_questions = play_trivia_game(user_id)
    # show_summary(correct_count, total_time_taken, total_questions)

if __name__ == '__main__':
    create_tables()
    # app = create_app()
    # app.run(debug=True)
    # drop_all_tables()



