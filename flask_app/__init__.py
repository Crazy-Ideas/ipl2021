import os

from flask import Flask
from flask_login import LoginManager

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

from config import Config

ipl_app: Flask = Flask(__name__)
ipl_app.config.from_object(Config)
login = LoginManager(ipl_app)
login.login_view = "login"
login.login_message = "Thanks for playing"

# noinspection PyPep8
from flask_app.user import login, logout
from flask_app import routes


@ipl_app.shell_context_processor
def make_shell_context() -> dict:
    from flask_app.bid import Bid
    from flask_app.match_score import MatchPlayer
    from flask_app.player import Player
    from flask_app.schedule import schedule
    from flask_app.team import UserTeam
    from flask_app.user import User
    from scoring import get_mock_score, get_score, get_match_player, update_match_points
    from game import save_file
    return {
        "Bid": Bid,
        "MatchPlayer": MatchPlayer,
        "Player": Player,
        "schedule": schedule,
        "UserTeam": UserTeam,
        "User": User,
        "get_mock_score": get_mock_score,
        "get_match_player": get_match_player,
        "get_score": get_score,
        "update_match_points": update_match_points,
        "save_file": save_file,
    }
