import os
from datetime import datetime

from dateutil.tz import gettz

from project_secrets import SecretConfig


class Config(SecretConfig):
    IMAGES = set(os.listdir("flask_app/static/images"))
    SCORE_2020 = 43682
    PLAYERS_2020 = 121
    COST_2020 = 49715
    TOTAL_COST = 60760
    PLAYERS_COST = 195
    BALANCE = 6750
    TOTAL_PLAYERS = 195
    USER_LIST = {"NZ": "Nayan Zaveri", "MB": "Manish Bhatt", "PP": "Pranay Patil", "VP": "Vinayak Patil",
                 "AG": "Avinash Gaikwad", "AN": "Ajit Nayak", "AS": "Arunesh Shah", "SS": "Sunny Saurabh",
                 "HJ": "Hitendra Jain"}
    USER_COUNT = len(USER_LIST)
    TEAMS = {"Mumbai Indians": "MI", "Chennai Super Kings": "CSK", "Delhi Capitals": "DC", "Kings XI Punjab": "KXIP",
             "Royal Challengers Bangalore": "RCB", "TBA": "TBD", "Kolkata Knight Riders": "KKR",
             "Sunrisers Hyderabad": "SRH", "Rajasthan Royals": "RR"}
    DATE, UNIQUE_ID, HOME_TEAM, AWAY_TEAM = "Date", "Unique Id", "Home Team", "Away Team"
    ROUND, MATCH_NO = "Gameweek", "Match No"
    NORMAL, CAPTAIN, SUB = "Normal", "Captain", "Sub"
    MULTIPLIER = {NORMAL: 1.0, CAPTAIN: 2.0, SUB: 0.5}
    INDIA_TZ = gettz("Asia/Kolkata")
    GAME_WEEK_START = datetime(year=2021, month=4, day=9, hour=19, tzinfo=INDIA_TZ)
    GAME_WEEK_2_CUT_OFF = datetime(year=2021, month=4, day=12, hour=19, tzinfo=INDIA_TZ)
    GAME_WEEK_9_CUT_OFF = datetime(year=2020, month=11, day=5, hour=19, tzinfo=INDIA_TZ)
    GAME_WEEK_10_CUT_OFF = datetime(year=2020, month=11, day=9, hour=19, tzinfo=INDIA_TZ)
    TEST_DATE = None
    USE_MOCK_SCORE = False


def today() -> datetime:
    return Config.TEST_DATE if Config.TEST_DATE else datetime.now(tz=Config.INDIA_TZ)
