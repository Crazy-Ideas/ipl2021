import os

from project_secrets import SecretConfig

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud-2020.json"


# noinspection PyPackageRequirements
from googleapiclient.discovery import build

SHEETS = build("sheets", "v4")

IPL_SHEET_ID = SecretConfig.IPL_SHEET_ID
PLAYER_RANGE = "Players!A2:J197"

def get_sheet_players():
    return SHEETS.spreadsheets().values() \
        .get(spreadsheetId=IPL_SHEET_ID, range=PLAYER_RANGE).execute() \
        .get("values", list())


def print_players():
    sheet_players = get_sheet_players()[1:]
    for player in sheet_players:
        print(player)
    return
