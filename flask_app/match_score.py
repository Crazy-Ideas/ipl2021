from typing import Dict, List, Tuple

from firestore_ci import FirestoreDocument

from config import Config


class ScoreData:

    def __init__(self, score_data: Dict):
        self.score_data = score_data

    def get_float_value(self, pid: str, key: str, score_type: str) -> float:
        player_record = next((player for team in self.score_data[score_type] for player in team["scores"]
                              if player["pid"] == pid), dict())
        if not player_record or key not in player_record:
            return 0.0
        try:
            value = float(player_record[key])
        except ValueError:
            value = 0.0
        return value

    def get_int_value(self, pid: str, key: str, score_type: str) -> int:
        return int(self.get_float_value(pid, key, score_type))

    def get_string_value(self, pid: str, key: str, score_type: str) -> str:
        player_record = next((player for team in self.score_data[score_type] for player in team["scores"]
                              if player["pid"] == pid), dict())
        if not player_record or key not in player_record:
            return str()
        return str(player_record[key])

    def get_runs(self, pid: str) -> int:
        return self.get_int_value(pid, "R", "batting")

    def get_fours(self, pid: str) -> int:
        return self.get_int_value(pid, "4s", "batting")

    def get_sixes(self, pid: str) -> int:
        return self.get_int_value(pid, "6s", "batting")

    def get_balls(self, pid: str) -> int:
        return self.get_int_value(pid, "B", "batting")

    def get_strike_rate(self, pid: str) -> float:
        return self.get_float_value(pid, "SR", "batting")

    def get_dismissal(self, pid: str) -> str:
        dismissal = self.get_string_value(pid, "dismissal", "batting")
        return str() if dismissal == "not out" else dismissal

    def get_overs(self, pid: str) -> float:
        return self.get_float_value(pid, "O", "bowling")

    def get_wickets(self, pid: str) -> int:
        return self.get_int_value(pid, "W", "bowling")

    def get_economy_rate(self, pid: str) -> float:
        return self.get_float_value(pid, "Econ", "bowling")

    def get_maidens(self, pid: str) -> int:
        return self.get_int_value(pid, "M", "bowling")

    def get_catches(self, pid: str) -> int:
        return self.get_int_value(pid, "catch", "fielding")

    def get_stumpings(self, pid: str) -> int:
        return self.get_int_value(pid, "stumped", "fielding")

    def get_runouts(self, pid: str) -> int:
        return self.get_int_value(pid, "runout", "fielding")

    def get_lbw(self, pid: str) -> int:
        return self.get_int_value(pid, "lbw", "fielding")

    def get_bowled(self, pid: str) -> int:
        return self.get_int_value(pid, "bowledSS", "fielding")

    def get_man_of_the_match(self, pid: str) -> bool:
        if "man-of-the-match" not in self.score_data:
            return False
        if "pid" not in self.score_data["man-of-the-match"]:
            return False
        if pid != self.score_data["man-of-the-match"]["pid"]:
            return False
        return True

    def get_playing_xi(self) -> List[Tuple[str, str]]:
        return [(player["pid"], player["name"]) for team in self.score_data["team"] for player in team["players"]]


class MatchPlayer(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.player_id: str = str()
        self.player_name: str = str()
        self.player_type: str = str()
        self.team: str = str()
        self.match_id: str = str()
        self.owner: str = str()
        self.gameweek: int = int()
        self.type: str = Config.NORMAL
        # Batting attributes
        self.runs: int = int()
        self.fours: int = int()
        self.sixes: int = int()
        self.balls: int = int()
        self.strike_rate: float = float()
        self.dismissal: str = str()  # Empty string if player is not out
        # Bowling attributes
        self.overs: float = float()
        self.wickets: int = int()
        self.economy_rate: float = float()
        self.maiden: int = int()
        self.lbw: int = int()
        self.bowled: int = int()
        # Fielding attributes
        self.catch: int = int()
        self.stumping: int = int()
        self.runout: int = int()
        # General attributes
        self.man_of_the_match: bool = bool()
        self.in_playing_xi: bool = bool()

    @property
    def batting_points(self) -> int:
        score = self.runs + self.fours * 1 + self.sixes * 2
        if self.runs >= 30:
            score += 4
        if self.runs >= 50:
            score += 8
        if self.runs >= 100:
            score += 16
        if self.runs == 0 and self.dismissal != str() and self.player_type and self.player_type not in Config.BOWLERS:
            score -= 2
        if self.balls >= 10:
            if self.strike_rate > 170.0:
                score += 6
            elif self.strike_rate > 150.0:
                score += 4
            elif self.strike_rate >= 130.0:
                score += 2
            elif self.strike_rate < 50.0:
                score -= 6
            elif self.strike_rate < 60.0:
                score -= 4
            elif self.strike_rate <= 70.0:
                score -= 2
        return score

    @property
    def bowling_points(self) -> int:
        score = self.wickets * 25 + self.maiden * 12 + self.lbw * 8 + self.bowled * 8
        if self.wickets >= 3:
            score += 4
        if self.wickets >= 4:
            score += 8
        if self.wickets >= 5:
            score += 16
        if self.overs >= 2.0:
            if self.economy_rate < 5.0:
                score += 6
            elif self.economy_rate < 6.0:
                score += 4
            elif self.economy_rate <= 7.0:
                score += 2
            elif self.economy_rate > 12.0:
                score -= 6
            elif self.economy_rate > 11.0:
                score -= 4
            elif self.economy_rate >= 10.0:
                score -= 2
        return score

    @property
    def fielding_points(self) -> int:
        score = self.catch * 10 + self.stumping * 10 + self.runout * 10
        if self.catch + self.stumping + self.runout >= 3:
            score += 4
        return score

    @property
    def man_of_the_match_points(self) -> int:
        return 10 if self.man_of_the_match else 0

    @property
    def playing_xi_points(self) -> int:
        return 4 if self.in_playing_xi else 0

    @property
    def general_points(self) -> int:
        return self.man_of_the_match_points + self.playing_xi_points

    @property
    def total_points(self) -> int:
        return self.batting_points + self.bowling_points + self.general_points + self.fielding_points

    @property
    def adjusted_points(self) -> float:
        if self.type == Config.CAPTAIN:
            return float(self.total_points * 2)
        elif self.type == Config.SUB:
            return self.total_points / 2
        return float(self.total_points)

    @property
    def display_class(self) -> str:
        if self.type == Config.CAPTAIN:
            return "table-success"
        elif self.type == Config.SUB:
            return "table-danger"
        return str()

    @property
    def owner_full_name(self) -> str:
        return Config.USER_LIST.get(self.owner.upper(), str())

    def update_scores(self, score_data: ScoreData):
        # Batting attributes
        self.runs = score_data.get_runs(self.player_id)
        self.fours = score_data.get_fours(self.player_id)
        self.sixes = score_data.get_sixes(self.player_id)
        self.balls: int = score_data.get_balls(self.player_id)
        self.strike_rate: float = score_data.get_strike_rate(self.player_id)
        self.dismissal: str = score_data.get_dismissal(self.player_id)
        # Bowling attributes
        self.overs = score_data.get_overs(self.player_id)
        self.wickets = score_data.get_wickets(self.player_id)
        self.economy_rate = score_data.get_economy_rate(self.player_id)
        self.maiden: int = score_data.get_maidens(self.player_id)
        self.lbw: int = score_data.get_lbw(self.player_id)
        self.bowled: int = score_data.get_bowled(self.player_id)
        # Fielding attributes
        self.catch: int = score_data.get_catches(self.player_id)
        self.stumping: int = score_data.get_stumpings(self.player_id)
        self.runout: int = score_data.get_runouts(self.player_id)
        # General attributes
        self.man_of_the_match = score_data.get_man_of_the_match(self.player_id)
        self.in_playing_xi = True


MatchPlayer.init("match_players")
