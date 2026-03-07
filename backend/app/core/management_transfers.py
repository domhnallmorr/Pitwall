import random
from typing import Any, Dict, List

from app.models.email import EmailCategory
from app.models.state import GameState


class CommercialManagerTransferManager:
    """
    AI transfer planner/announcer for commercial managers.
    Mirrors driver transfer flow but for single-seat management roles.
    """

    def recompute_ai_signings(self, state: GameState) -> List[Dict[str, Any]]:
        announced = list(state.announced_ai_cm_signings)
        blocked_teams = {s["team_id"] for s in announced}
        blocked_managers = {s["manager_id"] for s in announced}

        vacancies = self._get_ai_vacancies_for_next_season(state, blocked_teams)
        available = self._get_available_next_season_managers(state, blocked_managers)
        random.shuffle(vacancies)

        planned: List[Dict[str, Any]] = []
        taken_managers = set(blocked_managers)
        max_week = max((e.week for e in state.calendar.events), default=state.calendar.current_week)
        race_weeks = sorted(
            e.week for e in state.calendar.events if getattr(e.type, "value", e.type) == "RACE"
        )
        first_race_week = race_weeks[0] if race_weeks else state.calendar.current_week
        min_announce_week = max(state.calendar.current_week + 1, first_race_week + 1)
        min_announce_week = min(min_announce_week, max_week)

        for vacancy in vacancies:
            pool = [m for m in available if m.id not in taken_managers]
            if not pool:
                break
            manager = random.choice(pool)
            taken_managers.add(manager.id)
            planned.append(
                {
                    "team_id": vacancy["team_id"],
                    "team_name": vacancy["team_name"],
                    "seat": "commercial_manager_id",
                    "seat_label": "Commercial Manager",
                    "manager_id": manager.id,
                    "manager_name": manager.name,
                    "announce_week": random.randint(min_announce_week, max_week),
                    "announce_year": state.year,
                    "status": "planned",
                }
            )

        state.planned_ai_cm_signings = planned
        return planned

    def publish_due_announcements(self, state: GameState) -> List[Dict[str, Any]]:
        due = [
            s
            for s in state.planned_ai_cm_signings
            if s.get("announce_year") == state.year and s.get("announce_week") == state.calendar.current_week
        ]
        if not due:
            return []

        announced = list(state.announced_ai_cm_signings)
        announced_teams = {s["team_id"] for s in announced}
        announced_managers = {s["manager_id"] for s in announced}
        published: List[Dict[str, Any]] = []

        for signing in sorted(due, key=lambda s: s["team_name"]):
            if signing["team_id"] in announced_teams:
                continue
            if signing["manager_id"] in announced_managers:
                continue

            finalized = dict(signing)
            finalized["status"] = "announced"
            announced.append(finalized)
            announced_teams.add(finalized["team_id"])
            announced_managers.add(finalized["manager_id"])
            published.append(finalized)

            state.add_email(
                sender="Management Market Desk",
                subject=f"Management Signing Confirmed: {finalized['manager_name']} to {finalized['team_name']}",
                body=(
                    f"{finalized['team_name']} have confirmed the signing of {finalized['manager_name']} "
                    f"for next season ({state.year + 1}) as Commercial Manager."
                ),
                category=EmailCategory.SEASON,
            )

        state.announced_ai_cm_signings = announced
        due_ids = {
            (s["team_id"], s["manager_id"], s["announce_week"], s["announce_year"]) for s in due
        }
        state.planned_ai_cm_signings = [
            s
            for s in state.planned_ai_cm_signings
            if (s["team_id"], s["manager_id"], s["announce_week"], s["announce_year"]) not in due_ids
        ]
        return published

    def apply_new_season_transfers(self, state: GameState, announced_year: int) -> Dict[str, Any]:
        managers_by_id = {m.id: m for m in state.commercial_managers}
        teams_by_id = {t.id: t for t in state.teams}
        applied_signings: List[Dict[str, Any]] = []

        due_signings = [
            s
            for s in state.announced_ai_cm_signings
            if s.get("status") == "announced" and s.get("announce_year") == announced_year
        ]
        due_signings.sort(key=lambda s: s.get("team_id", 0))

        for signing in due_signings:
            team = teams_by_id.get(signing.get("team_id"))
            incoming = managers_by_id.get(signing.get("manager_id"))
            if team is None or incoming is None:
                continue

            current_id = team.commercial_manager_id
            current_manager = managers_by_id.get(current_id)
            if current_manager and current_manager.id != incoming.id:
                current_manager.team_id = None
                current_manager.contract_length = 0

            team.commercial_manager_id = incoming.id
            incoming.team_id = team.id
            incoming.contract_length = 2
            applied_signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "manager_id": incoming.id,
                    "manager_name": incoming.name,
                }
            )

        return {"applied_signings": applied_signings}

    def _get_ai_vacancies_for_next_season(
        self,
        state: GameState,
        blocked_teams: set[int],
    ) -> List[Dict[str, Any]]:
        managers_by_id = {m.id: m for m in state.commercial_managers}
        vacancies: List[Dict[str, Any]] = []

        for team in state.teams:
            if team.id == state.player_team_id:
                continue
            if team.id in blocked_teams:
                continue
            manager = managers_by_id.get(team.commercial_manager_id)
            if manager is None or not self._is_manager_retained_next_season(manager):
                vacancies.append({"team_id": team.id, "team_name": team.name})

        return vacancies

    def _get_available_next_season_managers(
        self,
        state: GameState,
        blocked_managers: set[int],
    ) -> List[Any]:
        available = []
        for manager in state.commercial_managers:
            if manager.id in blocked_managers:
                continue
            if manager.team_id is None or manager.contract_length == 1:
                available.append(manager)
        return available

    def _is_manager_retained_next_season(self, manager: Any) -> bool:
        return getattr(manager, "contract_length", 0) != 1

