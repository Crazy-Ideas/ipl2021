import json
import os
from datetime import datetime, timedelta
from typing import List

from dateutil import parser

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from config import Config, Image
from flask_app.schedule import Match
from flask_app.player import Player
from flask_app.user import User
from flask_app.bid import Bid

SHEETS = build("sheets", "v4")

IPL_SHEET_ID = Config.IPL_SHEET_ID
PLAYER_RANGE = "Players!A2:J197"
USER_RANGE = "Users!A1:D10"
PLAYER_IMAGE_RANGE = "PlayerImage!A1:B200"


def get_sheet_players():
    return SHEETS.spreadsheets().values() \
        .get(spreadsheetId=IPL_SHEET_ID, range=PLAYER_RANGE).execute() \
        .get("values", list())


def get_sheet_users():
    return SHEETS.spreadsheets().values() \
        .get(spreadsheetId=IPL_SHEET_ID, range=USER_RANGE).execute() \
        .get("values", list())


def update_missing_player_images():
    players: List[Player] = Player.objects.get()
    default_file = Image.url("some invalid file name")
    sheet_players = list()
    for player in players:
        if player.image == default_file:
            sheet_players.append([player.file_name, player.team])
    body = {"values": sheet_players}
    SHEETS.spreadsheets().values() \
        .update(spreadsheetId=IPL_SHEET_ID, range=PLAYER_IMAGE_RANGE, valueInputOption="USER_ENTERED", body=body) \
        .execute()
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


def _get_game_week(date: datetime) -> int:
    if date < Config.GAME_WEEK_2_CUT_OFF:
        return 1
    game_week_start = Config.GAME_WEEK_2_CUT_OFF
    max_game_weeks = 11
    for game_week in range(2, max_game_weeks):
        if game_week_start <= date < game_week_start + timedelta(days=7):
            return game_week
        game_week_start += timedelta(days=7)
    return max_game_weeks


def prepare_schedule():
    with open("source/schedule2021.json") as file:
        schedule = json.load(file)["matches"]
    matches: List[Match] = list()
    for match in schedule:
        if match["team-1"] not in Config.TEAMS or match["team-2"] not in Config.TEAMS:
            continue
        doc_match: Match = Match()
        doc_match.date = parser.parse(match["dateTimeGMT"]).astimezone(Config.INDIA_TZ)
        if doc_match.date.month <= 4 and match["team-1"] == "TBA":
            continue
        doc_match.unique_id = match["unique_id"]
        doc_match.home_team = Config.TEAMS[match["team-1"]]
        doc_match.away_team = Config.TEAMS[match["team-2"]]
        matches.append(doc_match)
    for index, match in enumerate(matches):
        match.number = index + 1
        match.game_week = _get_game_week(match.date)
        match.teams = [match.home_team, match.away_team]
    Match.objects.delete()
    Match.objects.create_all(Match.objects.to_dicts(matches))
    print(f"{len(matches)} matches created.")


def auction_on():
    users: List[User] = User.objects.get()
    for user in users:
        user.bidding = True
    User.objects.save_all(users)
    print(f"Auction turned ON for {len(users)} users.")


def auction_off():
    users: List[User] = User.objects.get()
    for user in users:
        user.bidding = False
    User.objects.save_all(users)
    print(f"Auction turned OFF for {len(users)} users.")


def auto_bid(username: str, status: bool = True):
    if not isinstance(status, bool):
        print("status parameter can be only True or False")
        return
    status_string = "ON" if status else "OFF"
    if username.lower() == "all":
        users: List[User] = User.objects.get()
        for user in users:
            user.auto_bid = status
            if status is False:
                continue
            if not user.bidding:
                continue
            player = Player.player_in_auction()
            if player and not Bid.objects.filter_by(player_name=player.name, username=user.username).first():
                Bid.submit_auto_bids(player, user)
                print(f"Auto bid submitted for username {user.username}.")
        User.objects.save_all(users)
        print(f"Auto bid turned {status_string} for {len(users)} users.")
        return
    user: User = User.objects.filter_by(username=username).first()
    if not user:
        print(f"username {username} not found in the database.")
        return
    user.auto_bid = status
    user.save()
    print(f"Auto bid turned {status_string} for username {username}.")
    if status is False:
        return
    if not user.bidding:
        return
    player = Player.player_in_auction()
    if player and not Bid.objects.filter_by(player_name=player.name, username=user.username).first():
        Bid.submit_auto_bids(player, user)
        print(f"Auto bid submitted for username {username}.")
    return


def reset_auction(auto_bid: bool = False, except_users: List[str] = None):
    users = User.objects.get()
    for user in users:
        user.balance = Config.BALANCE
        user.player_count = 0
        user.auto_bid = auto_bid ^ True if except_users and user.username in except_users else auto_bid
    User.objects.save_all(users)
    print(f"{len(users)} users balance update complete.")
    players: List[Player] = Player.objects.get()
    for player in players:
        player.reset_auction_status()
    Player.objects.save_all(players)
    print(f"{len(players)} players updated.")
    Bid.objects.delete()
    print("All bids deleted.")
