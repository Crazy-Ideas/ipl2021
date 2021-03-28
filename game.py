import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

# noinspection PyPackageRequirements
from googleapiclient.discovery import build

SHEETS = build("sheets", "v4")
IPL_SHEET_ID = "1xKPDB_MrwQf75jA_IxPnPwwl4jXniy1JRvIRd77h1FM"
PLAYER_RANGE = "Players!A1:I196"


def print_players():
    ipl_sheet = SHEETS.spreadsheets().values() \
        .get(spreadsheetId=IPL_SHEET_ID, range=PLAYER_RANGE).execute() \
        .get("values", list())
    print(ipl_sheet[0])
    for row in ipl_sheet[1:]:
        print(row)
    return
