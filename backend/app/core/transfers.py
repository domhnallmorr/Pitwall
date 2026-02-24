import random
from typing import Any, Dict, List

from app.models.email import EmailCategory
from app.models.state import GameState


class TransferManager:
    """
    Simple AI transfer planner/announcer for next season.
    Planned signings can be recomputed; announced signings remain locked.
    """

    def recompute_ai_signings(self, state: GameState) -> List[Dict[str, Any]]:
        announced = list(state.announced_ai_signings)
        blocked_seats = {(s["team_id"], s["seat"]) for s in announced}
        blocked_drivers = {s["driver_id"] for s in announced}

        vacancies = self._get_ai_vacancies_for_next_season(state, blocked_seats)
        available = self._get_available_next_season_drivers(state, blocked_drivers)
        random.shuffle(vacancies)

        planned: List[Dict[str, Any]] = []
        taken_drivers = set(blocked_drivers)
        max_week = max((e.week for e in state.calendar.events), default=state.calendar.current_week)
        race_weeks = sorted(
            e.week
            for e in state.calendar.events
            if getattr(e.type, "value", e.type) == "RACE"
        )
        first_race_week = race_weeks[0] if race_weeks else state.calendar.current_week
        min_announce_week = max(state.calendar.current_week + 1, first_race_week + 1)
        min_announce_week = min(min_announce_week, max_week)

        for vacancy in vacancies:
            pool = [d for d in available if d.id not in taken_drivers]
            if not pool:
                break
            driver = random.choice(pool)
            taken_drivers.add(driver.id)
            planned.append(
                {
                    "team_id": vacancy["team_id"],
                    "team_name": vacancy["team_name"],
                    "seat": vacancy["seat"],
                    "seat_label": vacancy["seat_label"],
                    "driver_id": driver.id,
                    "driver_name": driver.name,
                    "announce_week": random.randint(min_announce_week, max_week),
                    "announce_year": state.year,
                    "status": "planned",
                }
            )

        state.planned_ai_signings = planned
        return planned

    def publish_due_announcements(self, state: GameState) -> List[Dict[str, Any]]:
        due = [
            s for s in state.planned_ai_signings
            if s.get("announce_year") == state.year and s.get("announce_week") == state.calendar.current_week
        ]
        if not due:
            return []

        announced = list(state.announced_ai_signings)
        announced_seats = {(s["team_id"], s["seat"]) for s in announced}
        announced_drivers = {s["driver_id"] for s in announced}
        published: List[Dict[str, Any]] = []

        for signing in sorted(due, key=lambda s: (s["team_name"], s["seat"])):
            if (signing["team_id"], signing["seat"]) in announced_seats:
                continue
            if signing["driver_id"] in announced_drivers:
                continue

            finalized = dict(signing)
            finalized["status"] = "announced"
            announced.append(finalized)
            announced_seats.add((finalized["team_id"], finalized["seat"]))
            announced_drivers.add(finalized["driver_id"])
            published.append(finalized)

            state.add_email(
                sender="Driver Market Desk",
                subject=f"Transfer Confirmed: {finalized['driver_name']} to {finalized['team_name']}",
                body=(
                    f"{finalized['team_name']} have confirmed the signing of {finalized['driver_name']} "
                    f"for next season ({state.year + 1}), {finalized['seat_label']}."
                ),
                category=EmailCategory.SEASON,
            )

        state.announced_ai_signings = announced
        due_ids = {
            (s["team_id"], s["seat"], s["driver_id"], s["announce_week"], s["announce_year"])
            for s in due
        }
        state.planned_ai_signings = [
            s for s in state.planned_ai_signings
            if (s["team_id"], s["seat"], s["driver_id"], s["announce_week"], s["announce_year"]) not in due_ids
        ]
        return published

    def _get_ai_vacancies_for_next_season(
        self,
        state: GameState,
        blocked_seats: set[tuple[int, str]],
    ) -> List[Dict[str, Any]]:
        drivers_by_id = {d.id: d for d in state.drivers}
        vacancies: List[Dict[str, Any]] = []
        seat_map = [("driver1_id", "Driver 1"), ("driver2_id", "Driver 2")]

        for team in state.teams:
            if team.id == state.player_team_id:
                continue
            for seat, seat_label in seat_map:
                if (team.id, seat) in blocked_seats:
                    continue
                driver_id = getattr(team, seat)
                driver = drivers_by_id.get(driver_id)
                if driver is None or not self._is_driver_retained_next_season(driver, state.year):
                    vacancies.append(
                        {"team_id": team.id, "team_name": team.name, "seat": seat, "seat_label": seat_label}
                    )

        return vacancies

    def _get_available_next_season_drivers(
        self,
        state: GameState,
        blocked_drivers: set[int],
    ) -> List[Any]:
        available = []
        for driver in state.drivers:
            if driver.id in blocked_drivers:
                continue
            if not driver.active:
                continue
            if driver.retirement_year is not None and driver.retirement_year <= state.year:
                continue
            if driver.team_id is None or driver.contract_length == 1:
                available.append(driver)
        return available

    def _is_driver_retained_next_season(self, driver: Any, current_year: int) -> bool:
        if not driver.active:
            return False
        if driver.retirement_year is not None and driver.retirement_year <= current_year:
            return False
        if getattr(driver, "contract_length", 2) == 1:
            return False
        return True
