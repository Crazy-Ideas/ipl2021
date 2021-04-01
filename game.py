import os
from typing import List

from config import Config

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from flask_app.player import Player
from flask_app.user import User

SHEETS = build("sheets", "v4")

IPL_SHEET_ID = Config.IPL_SHEET_ID
PLAYER_RANGE = "Players!A2:J197"
USER_RANGE = "Users!A1:D10"


def get_sheet_players():
    return SHEETS.spreadsheets().values() \
        .get(spreadsheetId=IPL_SHEET_ID, range=PLAYER_RANGE).execute() \
        .get("values", list())


def get_sheet_users():
    return SHEETS.spreadsheets().values() \
        .get(spreadsheetId=IPL_SHEET_ID, range=USER_RANGE).execute() \
        .get("values", list())


def print_users():
    sheet_players = get_sheet_users()[1:]
    for player in sheet_players:
        print(player)
    return


def upload():
    print("Starting users upload.")
    User.objects.delete()
    print("All users deleted from firestore.")
    sheet_users = get_sheet_users()[1:]
    users = list()
    for sheet_user in sheet_users:
        user: User = User()
        user.username = sheet_user[0]
        user.set_password(sheet_user[1])
        user.name = sheet_user[2]
        user.email = sheet_user[3]
        user.balance = Config.BALANCE
        users.append(user)
    User.objects.create_all(User.objects.to_dicts(users))
    print(f"{len(users)} users created.\n")
    print("Starting players upload.")
    Player.objects.delete()
    print("All players deleted from firestore.")
    sheet_players = get_sheet_players()[1:]
    players = list()
    for sheet_player in sheet_players:
        player: Player = Player()
        player.name = sheet_player[0]
        player.status = sheet_player[1]
        player.country = sheet_player[2]
        player.type = sheet_player[3]
        player.base = int(sheet_player[4])
        player.team = sheet_player[5]
        player.cost = int(sheet_player[6])
        player.ipl2019_score = float(sheet_player[7])
        player.ipl2020_score = float(sheet_player[8])
        player.pid = sheet_player[9]
        players.append(player)
    Player.objects.create_all(Player.objects.to_dicts(players))
    print(f"{len(players)} players created.")


def update_rank():
    print("Calculating Ranks")
    players: List[Player] = Player.objects.get()
    players.sort(key=lambda player_item: -player_item.ipl2020_score)
    for player in players:
        ranked_player = next(rank_player for rank_player in players
                             if rank_player.ipl2020_score == player.ipl2020_score)
        player.ipl2020_rank = players.index(ranked_player) + 1
    players.sort(key=lambda player_item: -player_item.cost)
    for player in players:
        ranked_player = next(rank_player for rank_player in players if rank_player.cost == player.cost)
        player.cost_rank = players.index(ranked_player) + 1
    Player.objects.save_all(players)
    print(f"Ranks of {len(players)} players updated.")
