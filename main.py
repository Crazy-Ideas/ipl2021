import os
from datetime import datetime

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

from config import Config
from scoring import update_match_points, get_match_player
from flask_app.schedule import schedule
from flask_app.team import UserTeam


def set_test_date(data: dict):
    test_date = data.get('test_date', None)
    if not test_date:
        return
    Config.TEST_DATE = datetime.strptime(test_date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=Config.INDIA_TZ)
    return


def update_scores(data: dict, _):
    set_test_date(data)
    if not schedule.get_game_week():
        print("Error: SFL gameweek has not yet started")
        return
    update_match_points()
    return


def create_game_week(data: dict, _):
    set_test_date(data)
    UserTeam.create_game_week()
    return


def get_score(player_id: str, match_number: int):
    player = get_match_player(player_id, match_number)
    if not player:
        print(f"No score found for player {player_id} in match number {match_number}.")
        return
    print(f"Player: {player.player_name} ({player.team} - {player.player_type})\nTotal Points: {player.total_points}")
    print(f"Batting: {player.batting_points} (Runs: {player.runs}, Balls: {player.balls}, SR: {player.strike_rate}, "
          f"Dismissal: {player.dismissal if player.dismissal else 'not out'}, 4s: {player.fours}, 6s: {player.sixes})")
    print(f"Bowling: {player.bowling_points} (Overs: {player.overs}, Wickets: {player.wickets}, Maiden: {player.maiden}"
          f", ER: {player.economy_rate}, LBW: {player.lbw}, Bowled: {player.bowled})")
    print(f"Fielding: {player.fielding_points} (Catch: {player.catch}, Runout: {player.runout}, "
          f"Stumping: {player.stumping})")
    print(f"General: {player.general_points} (Playing XI: {player.playing_xi_points}, "
          f"MOM: {player.man_of_the_match_points})")
    return
