from datetime import datetime, timedelta

from dateutil.tz import gettz
from google.cloud.storage import Client

from project_secrets import SecretConfig


class Config(SecretConfig):
    SCORE_2020 = 43632
    PLAYERS_2020 = 120
    COST_2020 = 49515
    TOTAL_COST = 60560
    PLAYERS_COST = 145
    BALANCE = 6730
    TOTAL_PLAYERS = 194
    USER_LIST = {"NZ": "Nayan Zaveri", "MB": "Manish Bhatt", "PP": "Pranay Patil", "VP": "Vinayak Patil",
                 "AG": "Avinash Gaikwad", "AN": "Ajit Nayak", "AS": "Arunesh Shah", "SS": "Sunny Saurabh",
                 "HJ": "Hitendra Jain"}
    USER_COUNT = len(USER_LIST)
    TEAMS = {"Mumbai Indians": "MI", "Chennai Super Kings": "CSK", "Delhi Capitals": "DC", "Kings XI Punjab": "KXIP",
             "Royal Challengers Bangalore": "RCB", "TBA": "TBD", "Kolkata Knight Riders": "KKR",
             "Sunrisers Hyderabad": "SRH", "Rajasthan Royals": "RR"}
    PLAYER_STATUS = {"R": "Retained", "P": "Replaced", "N": "Auctioned - New", "A": "Auctioned - Existing",
                     "T": "Transferred"}
    ALL_ROUNDER, BATSMAN, WICKETKEEPER = "All-rounder", "Batsman", "Wicketkeeper"
    FAST_BOWLER, SPIN_BOWLER = "Fast bowler", "Spin bowler"
    PLAYER_TYPE = {ALL_ROUNDER, BATSMAN, WICKETKEEPER, FAST_BOWLER, SPIN_BOWLER}
    BOWLERS = {FAST_BOWLER, SPIN_BOWLER}
    NORMAL, CAPTAIN, SUB = "Normal", "Captain", "Sub"
    MULTIPLIER = {NORMAL: 1.0, CAPTAIN: 2.0, SUB: 0.5}
    INDIA_TZ = gettz("Asia/Kolkata")
    GAME_WEEK_START = datetime(year=2021, month=4, day=9, hour=19, tzinfo=INDIA_TZ)
    GAME_WEEK_2_CUT_OFF = datetime(year=2021, month=4, day=12, hour=19, tzinfo=INDIA_TZ)
    GAME_WEEK_9_CUT_OFF = GAME_WEEK_2_CUT_OFF + timedelta(days=7 * 7)
    GAME_WEEK_10_CUT_OFF = GAME_WEEK_9_CUT_OFF + timedelta(days=7)
    TEST_DATE = None
    USE_MOCK_SCORE = False
    EXT = {"jpg", "png"}


def today() -> datetime:
    return Config.TEST_DATE if Config.TEST_DATE else datetime.now(tz=Config.INDIA_TZ)


class Image:
    BUCKET = Client().bucket("ipl2021-players")
    IMAGE_FOLDER = "images"
    DEFAULT_FILE = f"{IMAGE_FOLDER}/default.jpg"

    @classmethod
    def url(cls, name: str) -> str:
        possible_file_names = [f"{cls.IMAGE_FOLDER}/{name}.{ext}" for ext in Config.EXT]
        file_path = next((file for file in possible_file_names if cls.BUCKET.blob(file).exists()), cls.DEFAULT_FILE)
        url = cls.BUCKET.blob(file_path).public_url
        return url
