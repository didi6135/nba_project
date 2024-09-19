from dataclasses import dataclass


@dataclass
class PlayerSeason:
    player_id: int
    season: int
    team: str
    points: int
    games: int
    twoPercent: float
    threePercent: float
    ATR: float
    PPG_ratio: float