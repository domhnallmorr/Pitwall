import random
from typing import Any, Dict, List

from app.models.email import EmailCategory
from app.models.state import GameState

from .shared import build_announcement_window


class TechnicalDirectorTransferManager:
    """
    AI transfer planner/announcer for technical directors.
    Mirrors commercial-manager transfer flow but for technical director roles.
    """

    def recompute_ai_signings(self, state: GameState) -> List[Dict[str, Any]]:
        announced = list(state.announced_ai_td_signings)
        blocked_teams = {s["team_id"] for s in announced}
        blocked_directors = {s["director_id"] for s in announced}

        vacancies = self._get_ai_vacancies_for_next_season(state, blocked_teams)
        available = self._get_available_next_season_directors(state, blocked_directors)
        random.shuffle(vacancies)

        planned: List[Dict[str, Any]] = []
        taken_directors = set(blocked_directors)
        min_announce_week, max_week = build_announcement_window(state)

        for vacancy in vacancies:
            pool = [d for d in available if d.id not in taken_directors]
            if not pool:
                break
            director = random.choice(pool)
            taken_directors.add(director.id)
            planned.append(
                {
                    "team_id": vacancy["team_id"],
                    "team_name": vacancy["team_name"],
                    "seat": "technical_director_id",
                    "seat_label": "Technical Director",
                    "director_id": director.id,
                    "director_name": director.name,
                    "announce_week": random.randint(min_announce_week, max_week),
                    "announce_year": state.year,
                    "status": "planned",
                }
            )

        state.planned_ai_td_signings = planned
        return planned

    def publish_due_announcements(self, state: GameState) -> List[Dict[str, Any]]:
        due = [
            s
            for s in state.planned_ai_td_signings
            if s.get("announce_year") == state.year and s.get("announce_week") == state.calendar.current_week
        ]
        if not due:
            return []

        announced = list(state.announced_ai_td_signings)
        announced_teams = {s["team_id"] for s in announced}
        announced_directors = {s["director_id"] for s in announced}
        published: List[Dict[str, Any]] = []

        for signing in sorted(due, key=lambda s: s["team_name"]):
            if signing["team_id"] in announced_teams:
                continue
            if signing["director_id"] in announced_directors:
                continue

            finalized = dict(signing)
            finalized["status"] = "announced"
            announced.append(finalized)
            announced_teams.add(finalized["team_id"])
            announced_directors.add(finalized["director_id"])
            published.append(finalized)

            state.add_email(
                sender="Management Market Desk",
                subject=f"Technical Director Signing Confirmed: {finalized['director_name']} to {finalized['team_name']}",
                body=(
                    f"{finalized['team_name']} have confirmed the signing of {finalized['director_name']} "
                    f"for next season ({state.year + 1}) as Technical Director."
                ),
                category=EmailCategory.SEASON,
            )

        state.announced_ai_td_signings = announced
        due_ids = {
            (s["team_id"], s["director_id"], s["announce_week"], s["announce_year"]) for s in due
        }
        state.planned_ai_td_signings = [
            s
            for s in state.planned_ai_td_signings
            if (s["team_id"], s["director_id"], s["announce_week"], s["announce_year"]) not in due_ids
        ]
        return published

    def apply_new_season_transfers(self, state: GameState, announced_year: int) -> Dict[str, Any]:
        directors_by_id = {d.id: d for d in state.technical_directors}
        teams_by_id = {t.id: t for t in state.teams}
        applied_signings: List[Dict[str, Any]] = []

        due_signings = [
            s
            for s in state.announced_ai_td_signings
            if s.get("status") == "announced" and s.get("announce_year") == announced_year
        ]
        due_signings.sort(key=lambda s: s.get("team_id", 0))

        for signing in due_signings:
            team = teams_by_id.get(signing.get("team_id"))
            incoming = directors_by_id.get(signing.get("director_id"))
            if team is None or incoming is None or not getattr(incoming, "active", True):
                continue

            current_id = team.technical_director_id
            current_director = directors_by_id.get(current_id)
            if current_director and current_director.id != incoming.id:
                current_director.team_id = None
                current_director.contract_length = 0

            team.technical_director_id = incoming.id
            incoming.team_id = team.id
            incoming.contract_length = 2
            applied_signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "director_id": incoming.id,
                    "director_name": incoming.name,
                }
            )

        return {"applied_signings": applied_signings}

    def sign_player_replacement(
        self,
        state: GameState,
        outgoing_director_id: int,
        incoming_director_id: int | None = None,
    ) -> Dict[str, Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if player_team.technical_director_id != outgoing_director_id:
            raise ValueError("Technical director is not assigned to the player team")

        outgoing = next((d for d in state.technical_directors if d.id == outgoing_director_id), None)
        if outgoing is None:
            raise ValueError("Technical director not found")
        if not getattr(outgoing, "active", True):
            raise ValueError("Technical director is retired")
        if outgoing.contract_length >= 2:
            raise ValueError("Technical director has 2 or more years remaining on contract")

        announced = list(state.announced_ai_td_signings)
        blocked_directors = {s["director_id"] for s in announced if s["team_id"] != player_team.id}

        existing = next((s for s in announced if s["team_id"] == player_team.id), None)
        if existing:
            announced.remove(existing)
            blocked_directors.discard(existing["director_id"])

        candidates = self.get_player_replacement_candidates(state, outgoing_director_id)
        if not candidates:
            raise ValueError("No available technical directors for replacement")
        if incoming_director_id is not None:
            signed_director = next((d for d in candidates if d.id == incoming_director_id), None)
            if signed_director is None:
                raise ValueError("Selected technical director is not available for replacement")
        else:
            signed_director = random.choice(candidates)

        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": "technical_director_id",
            "seat_label": "Technical Director",
            "director_id": signed_director.id,
            "director_name": signed_director.name,
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player",
        }
        announced.append(signing)
        state.announced_ai_td_signings = announced
        self.recompute_ai_signings(state)

        state.add_email(
            sender="Management Market Desk",
            subject=f"Technical Director Signed: {signed_director.name}",
            body=(
                f"You have signed {signed_director.name} for next season ({state.year + 1}) "
                f"as Technical Director, replacing {outgoing.name}."
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def get_player_replacement_candidates(self, state: GameState, outgoing_director_id: int) -> List[Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if player_team.technical_director_id != outgoing_director_id:
            raise ValueError("Technical director is not assigned to the player team")

        outgoing = next((d for d in state.technical_directors if d.id == outgoing_director_id), None)
        if outgoing is None:
            raise ValueError("Technical director not found")
        if not getattr(outgoing, "active", True):
            raise ValueError("Technical director is retired")
        if outgoing.contract_length >= 2:
            raise ValueError("Technical director has 2 or more years remaining on contract")

        announced = list(state.announced_ai_td_signings)
        blocked_directors = {s["director_id"] for s in announced if s["team_id"] != player_team.id}
        return [
            d
            for d in self._get_available_next_season_directors(state, blocked_directors)
            if d.id != outgoing_director_id
        ]

    def _get_ai_vacancies_for_next_season(
        self,
        state: GameState,
        blocked_teams: set[int],
    ) -> List[Dict[str, Any]]:
        directors_by_id = {d.id: d for d in state.technical_directors}
        vacancies: List[Dict[str, Any]] = []

        for team in state.teams:
            if team.id == state.player_team_id:
                continue
            if team.id in blocked_teams:
                continue
            director = directors_by_id.get(team.technical_director_id)
            if director is None or not self._is_director_retained_next_season(director):
                vacancies.append({"team_id": team.id, "team_name": team.name})

        return vacancies

    def _get_available_next_season_directors(
        self,
        state: GameState,
        blocked_directors: set[int],
    ) -> List[Any]:
        available = []
        for director in state.technical_directors:
            if director.id in blocked_directors:
                continue
            if not getattr(director, "active", True):
                continue
            if director.team_id is None or director.contract_length == 1:
                available.append(director)
        return available

    def _is_director_retained_next_season(self, director: Any) -> bool:
        if not getattr(director, "active", True):
            return False
        return getattr(director, "contract_length", 0) != 1
