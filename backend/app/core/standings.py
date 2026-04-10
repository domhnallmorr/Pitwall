from typing import List
from app.models.state import GameState
from app.models.driver import Driver
from app.models.team import Team

class StandingsManager:
    """
    Manages the championship standings and points for Drivers and Constructors.
    """
    COUNTBACK_POSITION_LIMIT = 30

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
        return sorted(eligible_drivers, key=lambda driver: self._driver_sort_key(game_state, driver))

    def get_constructor_standings(self, game_state: GameState) -> List[Team]:
        """
        Returns a list of teams sorted by points (descending), then FIA-style
        countback on race finishes (wins, 2nds, 3rds, etc).
        """
        return sorted(
            game_state.teams,
            key=lambda team: self._constructor_sort_key(game_state, team),
        )

    def build_driver_countback_notes(self, game_state: GameState, ordered_drivers: List[Driver]) -> dict[int, str]:
        notes: dict[int, str] = {}
        for index, driver in enumerate(ordered_drivers):
            note = None
            if index > 0 and ordered_drivers[index - 1].points == driver.points:
                note = self._best_result_note(self._driver_finish_position_counts(game_state, driver.id))
            elif index + 1 < len(ordered_drivers) and ordered_drivers[index + 1].points == driver.points:
                note = self._best_result_note(self._driver_finish_position_counts(game_state, driver.id))
            if note:
                notes[driver.id] = note
        return notes

    def build_constructor_countback_notes(self, game_state: GameState, ordered_teams: List[Team]) -> dict[int, str]:
        notes: dict[int, str] = {}
        for index, team in enumerate(ordered_teams):
            note = None
            if index > 0 and ordered_teams[index - 1].points == team.points:
                note = self._best_result_note(self._team_finish_position_counts(game_state, team.id))
            elif index + 1 < len(ordered_teams) and ordered_teams[index + 1].points == team.points:
                note = self._best_result_note(self._team_finish_position_counts(game_state, team.id))
            if note:
                notes[team.id] = note
        return notes

    def _constructor_sort_key(self, game_state: GameState, team: Team):
        position_counts = self._team_finish_position_counts(game_state, team.id)
        countback = tuple(-position_counts[position] for position in sorted(position_counts))
        return (-team.points, *countback, team.name)

    def _driver_sort_key(self, game_state: GameState, driver: Driver):
        position_counts = self._driver_finish_position_counts(game_state, driver.id)
        countback = tuple(-position_counts[position] for position in sorted(position_counts))
        return (-driver.points, *countback, driver.name)

    def _team_finish_position_counts(self, game_state: GameState, team_id: int) -> dict[int, int]:
        season_results = game_state.driver_season_results.get(game_state.year, {})
        team_driver_ids = {
            driver.id
            for driver in game_state.drivers
            if getattr(driver, "team_id", None) == team_id and getattr(driver, "active", True)
        }
        counts = {position: 0 for position in range(1, self.COUNTBACK_POSITION_LIMIT + 1)}

        for driver_id in team_driver_ids:
            for result in season_results.get(driver_id, []):
                position = result.get("position")
                if isinstance(position, int) and 0 < position <= self.COUNTBACK_POSITION_LIMIT:
                    counts[position] = counts.get(position, 0) + 1

        return counts

    def _driver_finish_position_counts(self, game_state: GameState, driver_id: int) -> dict[int, int]:
        season_results = game_state.driver_season_results.get(game_state.year, {})
        counts = {position: 0 for position in range(1, self.COUNTBACK_POSITION_LIMIT + 1)}

        for result in season_results.get(driver_id, []):
            position = result.get("position")
            if isinstance(position, int) and 0 < position <= self.COUNTBACK_POSITION_LIMIT:
                counts[position] = counts.get(position, 0) + 1

        return counts

    def _best_result_note(self, subject_counts: dict[int, int]) -> str | None:
        for position in range(1, self.COUNTBACK_POSITION_LIMIT + 1):
            subject = int(subject_counts.get(position, 0) or 0)
            if subject > 0:
                return f"x{subject} P{position}"
        return None
