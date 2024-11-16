
from dataclasses import dataclass

@dataclass
class SeasonStats:
    starts_this_season: int = 0
    points_this_season: int = 0
    poles_this_season: int = 0
    wins_this_season: int = 0
    podiums_this_season: int = 0
    dnfs_this_season: int = 0
    best_result_this_season: int = 0
    rnd_best_result_scored: int = 0 # the rnd at which the best result was scored
