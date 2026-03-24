import random
from typing import Any, Dict, List

from app.models.email import EmailCategory
from app.models.state import GameState

from .shared import build_announcement_window


class TitleSponsorTransferManager:
    """
    AI transfer planner/announcer for title sponsors.
    Mirrors the driver/staff transfer flow, but sponsor deals live on Team.
    """

    def recompute_ai_signings(self, state: GameState) -> List[Dict[str, Any]]:
        announced = list(state.announced_ai_title_sponsor_signings)
        blocked_teams = {s["team_id"] for s in announced}
        blocked_sponsors = {s["sponsor_id"] for s in announced}

        vacancies = self._get_ai_vacancies_for_next_season(state, blocked_teams)
        available = self._get_available_next_season_sponsors(state, blocked_sponsors)
        random.shuffle(vacancies)

        planned: List[Dict[str, Any]] = []
        taken_sponsors = set(blocked_sponsors)
        min_announce_week, max_week = build_announcement_window(state)

        for vacancy in vacancies:
            pool = [s for s in available if s.id not in taken_sponsors]
            if not pool:
                break
            sponsor = random.choice(pool)
            taken_sponsors.add(sponsor.id)
            planned.append(
                {
                    "team_id": vacancy["team_id"],
                    "team_name": vacancy["team_name"],
                    "seat": "title_sponsor_name",
                    "seat_label": "Title Sponsor",
                    "sponsor_id": sponsor.id,
                    "sponsor_name": sponsor.name,
                    "sponsor_wealth": sponsor.wealth,
                    "announce_week": random.randint(min_announce_week, max_week),
                    "announce_year": state.year,
                    "status": "planned",
                }
            )

        state.planned_ai_title_sponsor_signings = planned
        return planned

    def publish_due_announcements(self, state: GameState) -> List[Dict[str, Any]]:
        due = [
            s
            for s in state.planned_ai_title_sponsor_signings
            if s.get("announce_year") == state.year and s.get("announce_week") == state.calendar.current_week
        ]
        if not due:
            return []

        announced = list(state.announced_ai_title_sponsor_signings)
        announced_teams = {s["team_id"] for s in announced}
        announced_sponsors = {s["sponsor_id"] for s in announced}
        published: List[Dict[str, Any]] = []

        for signing in sorted(due, key=lambda s: s["team_name"]):
            if signing["team_id"] in announced_teams:
                continue
            if signing["sponsor_id"] in announced_sponsors:
                continue

            finalized = dict(signing)
            finalized["status"] = "announced"
            announced.append(finalized)
            announced_teams.add(finalized["team_id"])
            announced_sponsors.add(finalized["sponsor_id"])
            published.append(finalized)

            state.add_email(
                sender="Sponsorship Market Desk",
                subject=f"Title Sponsor Signing Confirmed: {finalized['sponsor_name']} to {finalized['team_name']}",
                body=(
                    f"{finalized['team_name']} have confirmed {finalized['sponsor_name']} "
                    f"as title sponsor for next season ({state.year + 1})."
                ),
                category=EmailCategory.SEASON,
            )

        state.announced_ai_title_sponsor_signings = announced
        due_ids = {
            (s["team_id"], s["sponsor_id"], s["announce_week"], s["announce_year"]) for s in due
        }
        state.planned_ai_title_sponsor_signings = [
            s
            for s in state.planned_ai_title_sponsor_signings
            if (s["team_id"], s["sponsor_id"], s["announce_week"], s["announce_year"]) not in due_ids
        ]
        return published

    def apply_new_season_transfers(self, state: GameState, announced_year: int) -> Dict[str, Any]:
        sponsors_by_id = {s.id: s for s in state.title_sponsors}
        teams_by_id = {t.id: t for t in state.teams}
        expiring_leavers: List[Dict[str, Any]] = []
        applied_signings: List[Dict[str, Any]] = []

        for team in state.teams:
            sponsor_name = getattr(team, "title_sponsor_name", None)
            contract_length = int(getattr(team, "title_sponsor_contract_length", 0) or 0)
            if not sponsor_name:
                team.title_sponsor_contract_length = 0
                team.title_sponsor_yearly = 0
                continue
            if contract_length > 1:
                team.title_sponsor_contract_length = contract_length - 1
                continue

            expiring_leavers.append(
                {"team_id": team.id, "team_name": team.name, "sponsor_name": sponsor_name}
            )
            team.title_sponsor_name = None
            team.title_sponsor_yearly = 0
            team.title_sponsor_contract_length = 0

        due_signings = [
            s
            for s in state.announced_ai_title_sponsor_signings
            if s.get("status") == "announced" and s.get("announce_year") == announced_year
        ]
        due_signings.sort(key=lambda s: s.get("team_id", 0))

        for signing in due_signings:
            team = teams_by_id.get(signing.get("team_id"))
            sponsor = sponsors_by_id.get(signing.get("sponsor_id"))
            if team is None or sponsor is None:
                continue

            team.title_sponsor_name = sponsor.name
            team.title_sponsor_yearly = sponsor.wealth
            team.title_sponsor_contract_length = 2
            applied_signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "sponsor_id": sponsor.id,
                    "sponsor_name": sponsor.name,
                }
            )

        return {
            "expiring_leavers": expiring_leavers,
            "applied_signings": applied_signings,
        }

    def sign_player_replacement(
        self,
        state: GameState,
        outgoing_sponsor_name: str,
        incoming_sponsor_id: int | None = None,
    ) -> Dict[str, Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if getattr(player_team, "title_sponsor_name", None) != outgoing_sponsor_name:
            raise ValueError("Title sponsor is not assigned to the player team")

        outgoing_contract_length = int(getattr(player_team, "title_sponsor_contract_length", 0) or 0)
        if outgoing_contract_length >= 2:
            raise ValueError("Title sponsor has 2 or more years remaining on contract")

        announced = list(state.announced_ai_title_sponsor_signings)
        blocked_sponsors = {s["sponsor_id"] for s in announced if s["team_id"] != player_team.id}

        existing = next((s for s in announced if s["team_id"] == player_team.id), None)
        if existing:
            announced.remove(existing)
            blocked_sponsors.discard(existing["sponsor_id"])

        candidates = self.get_player_replacement_candidates(state, outgoing_sponsor_name)
        if not candidates:
            raise ValueError("No available title sponsors for replacement")
        if incoming_sponsor_id is not None:
            signed_sponsor = next((s for s in candidates if s.id == incoming_sponsor_id), None)
            if signed_sponsor is None:
                raise ValueError("Selected title sponsor is not available for replacement")
        else:
            signed_sponsor = random.choice(candidates)

        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": "title_sponsor_name",
            "seat_label": "Title Sponsor",
            "sponsor_id": signed_sponsor.id,
            "sponsor_name": signed_sponsor.name,
            "sponsor_wealth": signed_sponsor.wealth,
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player",
        }
        announced.append(signing)
        state.announced_ai_title_sponsor_signings = announced
        self.recompute_ai_signings(state)

        state.add_email(
            sender="Sponsorship Market Desk",
            subject=f"Title Sponsor Signed: {signed_sponsor.name}",
            body=(
                f"You have signed {signed_sponsor.name} for next season ({state.year + 1}) "
                f"as title sponsor, replacing {outgoing_sponsor_name}."
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def get_player_replacement_candidates(self, state: GameState, outgoing_sponsor_name: str) -> List[Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if getattr(player_team, "title_sponsor_name", None) != outgoing_sponsor_name:
            raise ValueError("Title sponsor is not assigned to the player team")

        outgoing_contract_length = int(getattr(player_team, "title_sponsor_contract_length", 0) or 0)
        if outgoing_contract_length >= 2:
            raise ValueError("Title sponsor has 2 or more years remaining on contract")

        announced = list(state.announced_ai_title_sponsor_signings)
        blocked_sponsors = {s["sponsor_id"] for s in announced if s["team_id"] != player_team.id}
        outgoing = next((s for s in state.title_sponsors if s.name == outgoing_sponsor_name), None)
        outgoing_id = outgoing.id if outgoing else None
        return [
            s
            for s in self._get_available_next_season_sponsors(state, blocked_sponsors)
            if s.id != outgoing_id
        ]

    def _get_ai_vacancies_for_next_season(
        self,
        state: GameState,
        blocked_teams: set[int],
    ) -> List[Dict[str, Any]]:
        vacancies: List[Dict[str, Any]] = []

        for team in state.teams:
            if team.id == state.player_team_id:
                continue
            if team.id in blocked_teams:
                continue
            contract_length = int(getattr(team, "title_sponsor_contract_length", 0) or 0)
            sponsor_name = getattr(team, "title_sponsor_name", None)
            if not sponsor_name or contract_length == 1:
                vacancies.append({"team_id": team.id, "team_name": team.name})

        return vacancies

    def _get_available_next_season_sponsors(
        self,
        state: GameState,
        blocked_sponsors: set[int],
    ) -> List[Any]:
        retained_names = {
            getattr(team, "title_sponsor_name", None)
            for team in state.teams
            if getattr(team, "title_sponsor_name", None)
            and int(getattr(team, "title_sponsor_contract_length", 0) or 0) != 1
        }
        available = []
        for sponsor in state.title_sponsors:
            if sponsor.id in blocked_sponsors:
                continue
            if sponsor.name in retained_names:
                continue
            available.append(sponsor)
        return available
