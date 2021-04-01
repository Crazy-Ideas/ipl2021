import os
from typing import List

from db2020 import Player2020
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


def analyze_players():
    sheet_players = get_sheet_players()[1:]
    players: List[Player2020] = Player2020.objects.get()
    db_not_in_sheet = list()
    for player in players:
        sheet_player = next((sp for sp in sheet_players if sp[0] == player.name), None)
        if sheet_player:
            sheet_players.remove(sheet_player)
        else:
            db_not_in_sheet.append(player)
    if sheet_players:
        print("Following players are in the sheet but not in the db. Please confirm if they are new to IPL2021")
        for sheet_player in sheet_players:
            print(sheet_player)
        print("\n")
    if db_not_in_sheet:
        print("Following players are in the db but not in the sheet. Please confirm they are NOT playing IPL2021")
        for player in db_not_in_sheet:
            print(player)
    return


def update_players():
    sheet_players = get_sheet_players()
    players: List[Player2020] = Player2020.objects.get()
    for sheet_player in sheet_players[1:]:
        player = next((player for player in players if player.name == sheet_player[0]), None)
        if not player:
            continue
        sheet_player.extend([0] * (10 - len(sheet_player)))
        sheet_player[8] = player.score
        sheet_player[9] = player.pid
        print(sheet_player)
    body = {"values": sheet_players}
    SHEETS.spreadsheets().values() \
        .update(spreadsheetId=IPL_SHEET_ID, range=PLAYER_RANGE, valueInputOption="USER_ENTERED", body=body).execute()
    return
