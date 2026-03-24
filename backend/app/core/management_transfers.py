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
            if team is None or incoming is None or not getattr(incoming, "active", True):
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

    def sign_player_replacement(
        self,
        state: GameState,
        outgoing_manager_id: int,
        incoming_manager_id: int | None = None,
    ) -> Dict[str, Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if player_team.commercial_manager_id != outgoing_manager_id:
            raise ValueError("Commercial manager is not assigned to the player team")

        outgoing = next((m for m in state.commercial_managers if m.id == outgoing_manager_id), None)
        if outgoing is None:
            raise ValueError("Commercial manager not found")
        if not getattr(outgoing, "active", True):
            raise ValueError("Commercial manager is retired")
        if outgoing.contract_length >= 2:
            raise ValueError("Commercial manager has 2 or more years remaining on contract")

        announced = list(state.announced_ai_cm_signings)
        blocked_managers = {s["manager_id"] for s in announced if s["team_id"] != player_team.id}

        # Allow replacing any previously announced player signing for this seat.
        existing = next((s for s in announced if s["team_id"] == player_team.id), None)
        if existing:
            announced.remove(existing)
            blocked_managers.discard(existing["manager_id"])

        candidates = self.get_player_replacement_candidates(state, outgoing_manager_id)
        if not candidates:
            raise ValueError("No available commercial managers for replacement")
        if incoming_manager_id is not None:
            signed_manager = next((m for m in candidates if m.id == incoming_manager_id), None)
            if signed_manager is None:
                raise ValueError("Selected commercial manager is not available for replacement")
        else:
            signed_manager = random.choice(candidates)

        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": "commercial_manager_id",
            "seat_label": "Commercial Manager",
            "manager_id": signed_manager.id,
            "manager_name": signed_manager.name,
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player",
        }
        announced.append(signing)
        state.announced_ai_cm_signings = announced
        self.recompute_ai_signings(state)

        state.add_email(
            sender="Management Market Desk",
            subject=f"Commercial Manager Signed: {signed_manager.name}",
            body=(
                f"You have signed {signed_manager.name} for next season ({state.year + 1}) "
                f"as Commercial Manager, replacing {outgoing.name}."
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def get_player_replacement_candidates(self, state: GameState, outgoing_manager_id: int) -> List[Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if player_team.commercial_manager_id != outgoing_manager_id:
            raise ValueError("Commercial manager is not assigned to the player team")

        outgoing = next((m for m in state.commercial_managers if m.id == outgoing_manager_id), None)
        if outgoing is None:
            raise ValueError("Commercial manager not found")
        if not getattr(outgoing, "active", True):
            raise ValueError("Commercial manager is retired")
        if outgoing.contract_length >= 2:
            raise ValueError("Commercial manager has 2 or more years remaining on contract")

        announced = list(state.announced_ai_cm_signings)
        blocked_managers = {s["manager_id"] for s in announced if s["team_id"] != player_team.id}
        return [
            m
            for m in self._get_available_next_season_managers(state, blocked_managers)
            if m.id != outgoing_manager_id
        ]

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
            if not getattr(manager, "active", True):
                continue
            if manager.team_id is None or manager.contract_length == 1:
                available.append(manager)
        return available

    def _is_manager_retained_next_season(self, manager: Any) -> bool:
        if not getattr(manager, "active", True):
            return False
        return getattr(manager, "contract_length", 0) != 1


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
        max_week = max((e.week for e in state.calendar.events), default=state.calendar.current_week)
        race_weeks = sorted(
            e.week for e in state.calendar.events if getattr(e.type, "value", e.type) == "RACE"
        )
        first_race_week = race_weeks[0] if race_weeks else state.calendar.current_week
        min_announce_week = max(state.calendar.current_week + 1, first_race_week + 1)
        min_announce_week = min(min_announce_week, max_week)

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
        max_week = max((e.week for e in state.calendar.events), default=state.calendar.current_week)
        race_weeks = sorted(
            e.week for e in state.calendar.events if getattr(e.type, "value", e.type) == "RACE"
        )
        first_race_week = race_weeks[0] if race_weeks else state.calendar.current_week
        min_announce_week = max(state.calendar.current_week + 1, first_race_week + 1)
        min_announce_week = min(min_announce_week, max_week)

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
