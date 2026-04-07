import random
from typing import Any, Dict, List

from app.models.email import EmailCategory
from app.models.state import GameState

from .shared import build_announcement_window


class TeamPrincipalTransferManager:
    """
    AI transfer planner/announcer for team principals.
    Owner-principals are excluded from the market.
    """

    def recompute_ai_signings(self, state: GameState) -> List[Dict[str, Any]]:
        announced = list(state.announced_ai_tp_signings)
        blocked_teams = {s["team_id"] for s in announced}
        blocked_principals = {s["principal_id"] for s in announced}

        vacancies = self._get_ai_vacancies_for_next_season(state, blocked_teams)
        available = self._get_available_next_season_principals(state, blocked_principals)
        random.shuffle(vacancies)

        planned: List[Dict[str, Any]] = []
        taken_principals = set(blocked_principals)
        min_announce_week, max_week = build_announcement_window(state)

        for vacancy in vacancies:
            pool = [p for p in available if p.id not in taken_principals]
            if not pool:
                break
            principal = random.choice(pool)
            taken_principals.add(principal.id)
            planned.append(
                {
                    "team_id": vacancy["team_id"],
                    "team_name": vacancy["team_name"],
                    "seat": "team_principal_id",
                    "seat_label": "Team Principal",
                    "principal_id": principal.id,
                    "principal_name": principal.name,
                    "announce_week": random.randint(min_announce_week, max_week),
                    "announce_year": state.year,
                    "status": "planned",
                }
            )

        state.planned_ai_tp_signings = planned
        return planned

    def publish_due_announcements(self, state: GameState) -> List[Dict[str, Any]]:
        due = [
            s
            for s in state.planned_ai_tp_signings
            if s.get("announce_year") == state.year and s.get("announce_week") == state.calendar.current_week
        ]
        if not due:
            return []

        announced = list(state.announced_ai_tp_signings)
        announced_teams = {s["team_id"] for s in announced}
        announced_principals = {s["principal_id"] for s in announced}
        published: List[Dict[str, Any]] = []

        for signing in sorted(due, key=lambda s: s["team_name"]):
            if signing["team_id"] in announced_teams:
                continue
            if signing["principal_id"] in announced_principals:
                continue

            finalized = dict(signing)
            finalized["status"] = "announced"
            announced.append(finalized)
            announced_teams.add(finalized["team_id"])
            announced_principals.add(finalized["principal_id"])
            published.append(finalized)

            state.add_email(
                sender="Management Market Desk",
                subject=f"Team Principal Signing Confirmed: {finalized['principal_name']} to {finalized['team_name']}",
                body=(
                    f"{finalized['team_name']} have confirmed the signing of {finalized['principal_name']} "
                    f"for next season ({state.year + 1}) as Team Principal."
                ),
                category=EmailCategory.SEASON,
            )

        state.announced_ai_tp_signings = announced
        due_ids = {
            (s["team_id"], s["principal_id"], s["announce_week"], s["announce_year"]) for s in due
        }
        state.planned_ai_tp_signings = [
            s
            for s in state.planned_ai_tp_signings
            if (s["team_id"], s["principal_id"], s["announce_week"], s["announce_year"]) not in due_ids
        ]
        return published

    def apply_new_season_transfers(self, state: GameState, announced_year: int) -> Dict[str, Any]:
        principals_by_id = {p.id: p for p in state.team_principals}
        teams_by_id = {t.id: t for t in state.teams}
        applied_signings: List[Dict[str, Any]] = []

        due_signings = [
            s
            for s in state.announced_ai_tp_signings
            if s.get("status") == "announced" and s.get("announce_year") == announced_year
        ]
        due_signings.sort(key=lambda s: s.get("team_id", 0))

        for signing in due_signings:
            team = teams_by_id.get(signing.get("team_id"))
            incoming = principals_by_id.get(signing.get("principal_id"))
            if team is None or incoming is None or not getattr(incoming, "active", True):
                continue
            if getattr(incoming, "owns_team", False):
                continue

            current_id = team.team_principal_id
            current_principal = principals_by_id.get(current_id)
            if current_principal and current_principal.id != incoming.id:
                current_principal.team_id = None
                if not getattr(current_principal, "owns_team", False):
                    current_principal.contract_length = 0

            team.team_principal_id = incoming.id
            incoming.team_id = team.id
            incoming.contract_length = 2
            applied_signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "principal_id": incoming.id,
                    "principal_name": incoming.name,
                }
            )

        return {"applied_signings": applied_signings}

    def _get_ai_vacancies_for_next_season(
        self,
        state: GameState,
        blocked_teams: set[int],
    ) -> List[Dict[str, Any]]:
        principals_by_id = {p.id: p for p in state.team_principals}
        vacancies: List[Dict[str, Any]] = []

        for team in state.teams:
            if team.id == state.player_team_id:
                continue
            if team.id in blocked_teams:
                continue
            principal = principals_by_id.get(team.team_principal_id)
            if principal is None or not self._is_principal_retained_next_season(principal):
                vacancies.append({"team_id": team.id, "team_name": team.name})

        return vacancies

    def _get_available_next_season_principals(
        self,
        state: GameState,
        blocked_principals: set[int],
    ) -> List[Any]:
        available = []
        for principal in state.team_principals:
            if principal.id in blocked_principals:
                continue
            if not getattr(principal, "active", True):
                continue
            if getattr(principal, "owns_team", False):
                continue
            if principal.team_id is None or principal.contract_length == 1:
                available.append(principal)
        return available

    def _is_principal_retained_next_season(self, principal: Any) -> bool:
        if not getattr(principal, "active", True):
            return False
        if getattr(principal, "owns_team", False):
            return True
        return getattr(principal, "contract_length", 0) != 1
