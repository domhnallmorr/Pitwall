from typing import List
from app.models.state import GameState
from app.models.driver import Driver
from app.models.team import Team

class StandingsManager:
    """
    Manages the championship standings and points for Drivers and Constructors.
    """

    def reset_season(self, game_state: GameState) -> GameState:
        """
        Resets all driver and constructor points to zero for the start of a new season.
        """
        for driver in game_state.drivers:
            driver.points = 0
        
        for team in game_state.teams:
            team.points = 0
            
        return game_state

    def get_driver_standings(self, game_state: GameState) -> List[Driver]:
        """
        Returns active, team-assigned drivers sorted by points (descending).
        """
        eligible_drivers = [
            d for d in game_state.drivers
            if d.active and d.team_id is not None
        ]
        # Sort by points (desc), then by wins (todo), then by name (asc)
        return sorted(eligible_drivers, key=lambda d: (-d.points, d.name))

    def get_constructor_standings(self, game_state: GameState) -> List[Team]:
        """
        Returns a list of teams sorted by points (descending).
        """
        return sorted(game_state.teams, key=lambda t: (-t.points, t.name))
