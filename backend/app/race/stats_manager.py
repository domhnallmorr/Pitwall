from typing import Dict, Any, List

from app.models.state import GameState


class DriverStatsManager:
    """
    Central place for applying career stat updates from race outcomes.
    """

    def _event_key(self, state: GameState) -> str | None:
        event = state.calendar.current_event
        if event is None:
            return None
        return f"{state.year}_{event.week}_{event.name}"

    def _adjust_driver_stat(self, state: GameState, driver_id: int | None, stat_name: str, delta: int):
        if not driver_id or delta == 0:
            return
        driver = next((d for d in state.drivers if d.id == driver_id), None)
        if driver is None:
            return
        current_value = int(getattr(driver, stat_name, 0) or 0)
        setattr(driver, stat_name, max(0, current_value + delta))

    def _replace_award(self, state: GameState, awards: Dict[str, Any], award_key: str, driver_id: int | None, stat_name: str):
        previous_driver_id = awards.get(award_key)
        if previous_driver_id == driver_id:
            return
        self._adjust_driver_stat(state, previous_driver_id, stat_name, -1)
        self._adjust_driver_stat(state, driver_id, stat_name, 1)
        if driver_id:
            awards[award_key] = driver_id
        else:
            awards.pop(award_key, None)

    def _replace_driver_list_stat(
        self,
        state: GameState,
        awards: Dict[str, Any],
        award_key: str,
        driver_ids: List[int],
        stat_name: str,
    ):
        previous_ids = {int(driver_id) for driver_id in awards.get(award_key, [])}
        new_ids = {int(driver_id) for driver_id in driver_ids}
        for driver_id in previous_ids - new_ids:
            self._adjust_driver_stat(state, driver_id, stat_name, -1)
        for driver_id in new_ids - previous_ids:
            self._adjust_driver_stat(state, driver_id, stat_name, 1)
        awards[award_key] = sorted(new_ids)

    def apply_qualifying_results(self, state: GameState, qualifying_results: List[Dict[str, Any]]):
        event_key = self._event_key(state)
        if event_key is None:
            return
        awards = state.driver_stat_awards_by_event.setdefault(event_key, {})
        pole_row = next((row for row in qualifying_results if row.get("position") == 1), None)
        self._replace_award(
            state,
            awards,
            "pole_driver_id",
            pole_row.get("driver_id") if pole_row else None,
            "poles",
        )

    def apply_race_results(self, state: GameState, results: List[Dict[str, Any]]):
        """
        Update driver career stats based on race participants/results.
        """
        driver_lookup = {d.id: d for d in state.drivers}
        event = state.calendar.current_event
        country = "Unknown"
        race_round = None
        if event:
            circuit = next((c for c in state.circuits if c.name == event.name), None)
            if circuit:
                country = circuit.country
            race_round = sum(
                1 for e in state.calendar.events
                if e.type.value == "RACE" and e.week <= event.week
            )

        year_bucket = state.driver_season_results.setdefault(state.year, {})
        event_key = self._event_key(state)
        awards = state.driver_stat_awards_by_event.setdefault(event_key, {}) if event_key else None
        participant_ids = [int(entry["driver_id"]) for entry in results if entry.get("driver_id") in driver_lookup]
        podium_ids = [
            int(entry["driver_id"])
            for entry in results
            if entry.get("driver_id") in driver_lookup
            and isinstance(entry.get("position"), int)
            and 1 <= int(entry["position"]) <= 3
        ]
        winner_row = next((entry for entry in results if entry.get("position") == 1), None)
        fastest_lap_row = next((entry for entry in results if entry.get("fastest_lap")), None)

        if awards is not None:
            self._replace_driver_list_stat(state, awards, "participants", participant_ids, "race_starts")
            self._replace_driver_list_stat(state, awards, "podium_driver_ids", podium_ids, "podiums")
            self._replace_award(
                state,
                awards,
                "winner_driver_id",
                winner_row.get("driver_id") if winner_row else None,
                "wins",
            )
            self._replace_award(
                state,
                awards,
                "fastest_lap_driver_id",
                fastest_lap_row.get("driver_id") if fastest_lap_row else None,
                "fastest_laps",
            )
        else:
            for driver_id in participant_ids:
                self._adjust_driver_stat(state, driver_id, "race_starts", 1)
            for driver_id in podium_ids:
                self._adjust_driver_stat(state, driver_id, "podiums", 1)
            self._adjust_driver_stat(state, winner_row.get("driver_id") if winner_row else None, "wins", 1)
            self._adjust_driver_stat(
                state,
                fastest_lap_row.get("driver_id") if fastest_lap_row else None,
                "fastest_laps",
                1,
            )

        for entry in results:
            driver = driver_lookup.get(entry.get("driver_id"))
            if driver:
                # Track per-season race results for driver profile pages.
                if event and race_round is not None:
                    driver_bucket = year_bucket.setdefault(driver.id, [])
                    new_result = {
                        "round": race_round,
                        "event_name": event.name,
                        "country": country,
                        "position": entry.get("position", 0),
                        "status": entry.get("status", "FINISHED"),
                    }
                    # Upsert by round to avoid duplicates if race is re-simulated.
                    replaced = False
                    for idx, existing in enumerate(driver_bucket):
                        if existing.get("round") == race_round:
                            driver_bucket[idx] = new_result
                            replaced = True
                            break
                    if not replaced:
                        driver_bucket.append(new_result)
