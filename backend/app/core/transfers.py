import random
from typing import Any, Dict, List

from app.models.enums import DriverRole
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
        teams_by_id = {team.id: team for team in state.teams}

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
            team = teams_by_id.get(vacancy["team_id"])
            pool = [
                d for d in available
                if d.id not in taken_drivers and d.id != vacancy.get("outgoing_driver_id")
            ]
            if not pool:
                break
            driver = self._pick_driver_for_vacancy(team, vacancy, pool)
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

    def _pick_driver_for_vacancy(self, team: Any, vacancy: Dict[str, Any], pool: List[Any]) -> Any:
        scored_pool = sorted(
            pool,
            key=lambda driver: self._score_driver_for_vacancy(team, vacancy, driver),
            reverse=True,
        )
        shortlist = scored_pool[: min(3, len(scored_pool))]
        return random.choice(shortlist)

    def _team_desirability(self, state: GameState, team: Any) -> int:
        current_strength = getattr(team, "car_speed", 50)
        baseline_strength = next(
            (
                snapshot.get("CarRating", current_strength)
                for snapshot in state.grid_snapshots.get(1998, [])
                if snapshot.get("Team") == getattr(team, "name", None)
            ),
            current_strength,
        )
        principal_skill = 50
        principal_id = getattr(team, "team_principal_id", None)
        if principal_id is not None:
            principal = next((p for p in state.team_principals if p.id == principal_id), None)
            if principal is not None:
                principal_skill = principal.skill

        desirability = round((current_strength * 0.5) + (baseline_strength * 0.35) + (principal_skill * 0.15))
        return desirability

    def _vacancy_strategy(self, team: Any, vacancy: Dict[str, Any]) -> str:
        team_strength = vacancy.get("team_desirability", getattr(team, "car_speed", 50) if team is not None else 50)
        lead_seat = vacancy.get("seat") == "driver1_id"
        outgoing_speed = vacancy.get("outgoing_driver_speed", 0)
        outgoing_pay_driver = vacancy.get("outgoing_driver_pay_driver", False)

        if not lead_seat and team_strength <= 45:
            return "cash_seat"
        if outgoing_pay_driver and not lead_seat:
            return "cash_seat"
        if lead_seat and (team_strength >= 60 or outgoing_speed < max(58, team_strength - 6)):
            return "upgrade"
        if not lead_seat and outgoing_speed < max(48, team_strength - 10):
            return "upgrade"
        return "hold"

    def _score_driver_for_vacancy(self, team: Any, vacancy: Dict[str, Any], driver: Any) -> int:
        lead_seat = vacancy.get("seat") == "driver1_id"
        team_strength = vacancy.get("team_desirability", getattr(team, "car_speed", 50) if team is not None else 50)
        strategy = self._vacancy_strategy(team, vacancy)

        if strategy == "upgrade":
            target_speed = max(50, team_strength + (7 if lead_seat else 0))
        elif strategy == "cash_seat":
            target_speed = max(42, team_strength - (8 if lead_seat else 12))
        else:
            outgoing_speed = vacancy.get("outgoing_driver_speed", team_strength)
            target_speed = max(45, outgoing_speed + (2 if lead_seat else -1))

        score = driver.speed * 4
        if driver.speed < target_speed:
            score -= (target_speed - driver.speed) * 8
        else:
            score += min(10, driver.speed - target_speed) * 3

        if driver.age <= 25:
            score += 8
        elif driver.age <= 31:
            score += 4
        elif driver.age >= 39:
            score -= 16
        elif driver.age >= 36:
            score -= 8

        if driver.pay_driver:
            if strategy == "cash_seat" and not lead_seat:
                score += 18 if team_strength <= 45 else 10
            elif lead_seat:
                score -= 18
            elif team_strength <= 45:
                score += 16
            elif team_strength <= 55:
                score += 4
            else:
                score -= 10

        if driver.team_id is None:
            score += 3

        outgoing_speed = vacancy.get("outgoing_driver_speed")
        if strategy == "hold" and outgoing_speed is not None:
            score -= abs(driver.speed - outgoing_speed) * 8
        elif strategy == "upgrade" and outgoing_speed is not None and driver.speed > outgoing_speed:
            score += min(12, driver.speed - outgoing_speed) * 2

        return score

    def _should_retain_driver(self, team: Any, seat: str, driver: Any) -> bool:
        if not driver.active:
            return False

        team_strength = getattr(team, "car_speed", 50)
        lead_seat = seat == "driver1_id"
        minimum_speed = max(58, team_strength - 2) if lead_seat else max(50, team_strength - 8)
        age_limit = 34 if lead_seat else 36

        if driver.pay_driver and (lead_seat or team_strength >= 55):
            return False
        if driver.age > age_limit:
            return False
        return driver.speed >= minimum_speed

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

    def sign_player_replacement(
        self,
        state: GameState,
        outgoing_driver_id: int,
        incoming_driver_id: int | None = None,
    ) -> Dict[str, Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")

        seat, seat_label, outgoing = self._get_player_seat_and_driver(state, outgoing_driver_id, player_team.id)
        if seat is None or outgoing is None:
            raise ValueError("Driver is not in a player team race seat")
        if outgoing.contract_length >= 2:
            raise ValueError("Driver has 2 or more years remaining on contract")

        announced = list(state.announced_ai_signings)
        announced_by_seat = {(s["team_id"], s["seat"]): s for s in announced}
        blocked_drivers = {s["driver_id"] for s in announced}
        # Player can replace an existing player signing for the same seat.
        existing = announced_by_seat.get((player_team.id, seat))
        if existing:
            announced.remove(existing)
            blocked_drivers.discard(existing["driver_id"])

        candidates = self.get_player_replacement_candidates(state, outgoing_driver_id)
        if not candidates:
            raise ValueError("No available drivers for replacement")
        if incoming_driver_id is not None:
            signed_driver = next((d for d in candidates if d.id == incoming_driver_id), None)
            if signed_driver is None:
                raise ValueError("Selected driver is not available for replacement")
        else:
            signed_driver = random.choice(candidates)
        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": seat,
            "seat_label": seat_label,
            "driver_id": signed_driver.id,
            "driver_name": signed_driver.name,
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player",
        }
        announced.append(signing)
        state.announced_ai_signings = announced
        # Recompute AI plans around player's confirmed choice.
        self.recompute_ai_signings(state)

        state.add_email(
            sender="Driver Market Desk",
            subject=f"Driver Signed: {signed_driver.name}",
            body=(
                f"You have signed {signed_driver.name} for next season ({state.year + 1}) "
                f"as {seat_label}, replacing {outgoing.name}."
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def get_player_replacement_candidates(self, state: GameState, outgoing_driver_id: int) -> List[Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        seat, _, outgoing = self._get_player_seat_and_driver(state, outgoing_driver_id, player_team.id)
        if seat is None or outgoing is None:
            raise ValueError("Driver is not in a player team race seat")
        if outgoing.contract_length >= 2:
            raise ValueError("Driver has 2 or more years remaining on contract")

        announced = list(state.announced_ai_signings)
        blocked_drivers = {s["driver_id"] for s in announced if s["team_id"] != player_team.id}
        return [
            d for d in self._get_available_next_season_drivers(state, blocked_drivers)
            if d.id != outgoing_driver_id
        ]

    def apply_new_season_transfers(self, state: GameState, announced_year: int) -> Dict[str, Any]:
        """
        Apply contract rollover and announced transfer deals at season transition.
        Returns a summary of expiries and applied deals.
        """
        drivers_by_id = {d.id: d for d in state.drivers}
        teams_by_id = {t.id: t for t in state.teams}
        expiring_leavers: List[Dict[str, Any]] = []
        applied_signings: List[Dict[str, Any]] = []

        # 1. Resolve contract rollover first.
        for team in state.teams:
            for seat in ("driver1_id", "driver2_id"):
                driver_id = getattr(team, seat)
                driver = drivers_by_id.get(driver_id)
                if driver is None or not driver.active:
                    continue
                if driver.contract_length > 1:
                    driver.contract_length -= 1
                    continue

                # Contract expired (1 year left) or already at 0.
                setattr(team, seat, None)
                driver.team_id = None
                driver.role = None
                driver.contract_length = 0
                expiring_leavers.append(
                    {"driver_id": driver.id, "driver_name": driver.name, "team_id": team.id, "team_name": team.name}
                )

        # 2. Apply announced deals for this transfer year.
        due_signings = [
            s for s in state.announced_ai_signings
            if s.get("status") == "announced" and s.get("announce_year") == announced_year
        ]
        due_signings.sort(key=lambda s: (s.get("team_id", 0), s.get("seat", "")))

        for signing in due_signings:
            team = teams_by_id.get(signing.get("team_id"))
            seat = signing.get("seat")
            incoming = drivers_by_id.get(signing.get("driver_id"))
            if team is None or seat not in {"driver1_id", "driver2_id"} or incoming is None or not incoming.active:
                continue

            # Evict any current occupant from this seat.
            current_id = getattr(team, seat)
            current_driver = drivers_by_id.get(current_id)
            if current_driver and current_driver.id != incoming.id:
                current_driver.team_id = None
                current_driver.role = None
                current_driver.contract_length = 0

            setattr(team, seat, incoming.id)
            incoming.team_id = team.id
            incoming.role = DriverRole.DRIVER_1 if seat == "driver1_id" else DriverRole.DRIVER_2
            # Keep it simple for now: fresh signing receives a default 2-year deal.
            incoming.contract_length = 2
            applied_signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "seat": seat,
                    "driver_id": incoming.id,
                    "driver_name": incoming.name,
                }
            )

        return {
            "expiring_leavers": expiring_leavers,
            "applied_signings": applied_signings,
        }

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
                if driver is None:
                    vacancies.append(
                        {"team_id": team.id, "team_name": team.name, "seat": seat, "seat_label": seat_label}
                    )
                    continue
                if driver.contract_length == 1 and self._should_retain_driver(team, seat, driver):
                    continue
                if self._is_driver_retained_next_season(driver, state.year):
                    continue
                vacancies.append(
                    {
                        "team_id": team.id,
                        "team_name": team.name,
                        "seat": seat,
                        "seat_label": seat_label,
                        "team_desirability": self._team_desirability(state, team),
                        "outgoing_driver_id": driver.id,
                        "outgoing_driver_name": driver.name,
                        "outgoing_driver_speed": driver.speed,
                        "outgoing_driver_pay_driver": driver.pay_driver,
                    }
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

    def _get_player_seat_and_driver(self, state: GameState, driver_id: int, player_team_id: int):
        by_id = {d.id: d for d in state.drivers}
        if driver_id == next((t.driver1_id for t in state.teams if t.id == player_team_id), None):
            return "driver1_id", "Driver 1", by_id.get(driver_id)
        if driver_id == next((t.driver2_id for t in state.teams if t.id == player_team_id), None):
            return "driver2_id", "Driver 2", by_id.get(driver_id)
        return None, None, None
