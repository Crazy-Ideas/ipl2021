import os
from typing import Optional, Dict

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud-2020.json"

from firestore_ci import FirestoreDocument


class Player2020(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = str()
        self.cost: int = 0
        self.base: int = 0
        self.country: str = str()
        self.type: str = str()
        self.ipl2019_score: float = 0.0
        self.team: str = str()
        self.score: int = 0
        self.ipl2019_rank: int = 0
        self.cost_rank: int = 0
        self.owner: Optional[str] = None
        self.price: int = 0
        self.auction_status: str = str()
        self.bid_order: int = 0
        self._sbp_cost: int = 0
        self.ipl_name: str = str()
        self.pid: str = str()
        self.scores: Dict[str, int] = dict()

    def __repr__(self) -> str:
        return f"{self.name}:{self.team}:{self.ipl_name}:{self.pid}:{self.score}"


Player2020.init("players")
