import random
from typing import Any, Dict, List

from app.models.email import EmailCategory
from app.models.state import GameState

from .shared import build_announcement_window


class EngineSupplierTransferManager:
    """
    AI transfer planner/announcer for engine suppliers.
    Ferano-style self-built engine teams are excluded from the market.
    """

    CUSTOMER_COST = 4_500_000

    def recompute_ai_signings(self, state: GameState) -> List[Dict[str, Any]]:
        announced = list(state.announced_ai_engine_supplier_signings)
        blocked_teams = {s["team_id"] for s in announced}

        vacancies = self._get_ai_vacancies_for_next_season(state, blocked_teams)
        available = self._get_available_next_season_suppliers(state)
        random.shuffle(vacancies)

        planned: List[Dict[str, Any]] = []
        min_announce_week, max_week = build_announcement_window(state)

        for vacancy in vacancies:
            if not available:
                break
            supplier = random.choice(available)
            deal_type, yearly_cost = self._pick_deal_for_team(vacancy["team"])
            planned.append(
                {
                    "team_id": vacancy["team_id"],
                    "team_name": vacancy["team_name"],
                    "seat": "engine_supplier_name",
                    "seat_label": "Engine Supplier",
                    "supplier_id": supplier.id,
                    "supplier_name": supplier.name,
                    "deal_type": deal_type,
                    "yearly_cost": yearly_cost,
                    "announce_week": random.randint(min_announce_week, max_week),
                    "announce_year": state.year,
                    "status": "planned",
                }
            )

        state.planned_ai_engine_supplier_signings = planned
        return planned

    def publish_due_announcements(self, state: GameState) -> List[Dict[str, Any]]:
        due = [
            s
            for s in state.planned_ai_engine_supplier_signings
            if s.get("announce_year") == state.year and s.get("announce_week") == state.calendar.current_week
        ]
        if not due:
            return []

        announced = list(state.announced_ai_engine_supplier_signings)
        announced_teams = {s["team_id"] for s in announced}
        published: List[Dict[str, Any]] = []

        for signing in sorted(due, key=lambda s: s["team_name"]):
            if signing["team_id"] in announced_teams:
                continue

            finalized = dict(signing)
            finalized["status"] = "announced"
            announced.append(finalized)
            announced_teams.add(finalized["team_id"])
            published.append(finalized)

            state.add_email(
                sender="Supplier Market Desk",
                subject=f"Engine Supplier Signing Confirmed: {finalized['supplier_name']} to {finalized['team_name']}",
                body=(
                    f"{finalized['team_name']} have confirmed {finalized['supplier_name']} "
                    f"as engine supplier for next season ({state.year + 1}) on a {finalized['deal_type']} deal."
                ),
                category=EmailCategory.SEASON,
            )

        state.announced_ai_engine_supplier_signings = announced
        due_ids = {
            (s["team_id"], s["supplier_id"], s["announce_week"], s["announce_year"]) for s in due
        }
        state.planned_ai_engine_supplier_signings = [
            s
            for s in state.planned_ai_engine_supplier_signings
            if (s["team_id"], s["supplier_id"], s["announce_week"], s["announce_year"]) not in due_ids
        ]
        return published

    def apply_new_season_transfers(self, state: GameState, announced_year: int) -> Dict[str, Any]:
        suppliers_by_id = {s.id: s for s in state.engine_suppliers}
        teams_by_id = {t.id: t for t in state.teams}
        expiring_leavers: List[Dict[str, Any]] = []
        applied_signings: List[Dict[str, Any]] = []

        for team in state.teams:
            if getattr(team, "builds_own_engine", False):
                team.engine_supplier_contract_length = 0
                team.engine_supplier_deal = "works"
                team.engine_supplier_yearly_cost = 0
                continue

            supplier_name = getattr(team, "engine_supplier_name", None)
            contract_length = int(getattr(team, "engine_supplier_contract_length", 0) or 0)
            if not supplier_name:
                team.engine_supplier_contract_length = 0
                team.engine_supplier_deal = None
                team.engine_supplier_yearly_cost = 0
                continue
            if contract_length > 1:
                team.engine_supplier_contract_length = contract_length - 1
                continue

            expiring_leavers.append(
                {"team_id": team.id, "team_name": team.name, "supplier_name": supplier_name}
            )
            team.engine_supplier_name = None
            team.engine_supplier_deal = None
            team.engine_supplier_yearly_cost = 0
            team.engine_supplier_contract_length = 0

        due_signings = [
            s
            for s in state.announced_ai_engine_supplier_signings
            if s.get("status") == "announced" and s.get("announce_year") == announced_year
        ]
        due_signings.sort(key=lambda s: s.get("team_id", 0))

        for signing in due_signings:
            team = teams_by_id.get(signing.get("team_id"))
            supplier = suppliers_by_id.get(signing.get("supplier_id"))
            if team is None or supplier is None:
                continue
            if getattr(team, "builds_own_engine", False):
                continue

            team.engine_supplier_name = supplier.name
            team.engine_supplier_deal = signing.get("deal_type")
            team.engine_supplier_yearly_cost = int(signing.get("yearly_cost") or 0)
            team.engine_supplier_contract_length = 2
            applied_signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "supplier_id": supplier.id,
                    "supplier_name": supplier.name,
                    "deal_type": team.engine_supplier_deal,
                }
            )

        return {
            "expiring_leavers": expiring_leavers,
            "applied_signings": applied_signings,
        }

    def sign_player_replacement(
        self,
        state: GameState,
        outgoing_supplier_name: str,
        incoming_supplier_id: int | None = None,
    ) -> Dict[str, Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if getattr(player_team, "builds_own_engine", False):
            raise ValueError("Self-built engine programmes cannot be replaced")
        if getattr(player_team, "engine_supplier_name", None) != outgoing_supplier_name:
            raise ValueError("Engine supplier is not assigned to the player team")

        outgoing_contract_length = int(getattr(player_team, "engine_supplier_contract_length", 0) or 0)
        if outgoing_contract_length >= 2:
            raise ValueError("Engine supplier has 2 or more years remaining on contract")

        announced = list(state.announced_ai_engine_supplier_signings)
        existing = next((s for s in announced if s["team_id"] == player_team.id), None)
        if existing:
            announced.remove(existing)

        candidates = self.get_player_replacement_candidates(state, outgoing_supplier_name)
        if not candidates:
            raise ValueError("No available engine suppliers for replacement")
        if incoming_supplier_id is not None:
            signed_supplier = next((s for s in candidates if s.id == incoming_supplier_id), None)
            if signed_supplier is None:
                raise ValueError("Selected engine supplier is not available for replacement")
        else:
            signed_supplier = random.choice(candidates)

        deal_type, yearly_cost = self._pick_deal_for_team(player_team)
        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": "engine_supplier_name",
            "seat_label": "Engine Supplier",
            "supplier_id": signed_supplier.id,
            "supplier_name": signed_supplier.name,
            "deal_type": deal_type,
            "yearly_cost": yearly_cost,
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player",
        }
        announced.append(signing)
        state.announced_ai_engine_supplier_signings = announced
        self.recompute_ai_signings(state)

        state.add_email(
            sender="Supplier Market Desk",
            subject=f"Engine Supplier Signed: {signed_supplier.name}",
            body=(
                f"You have signed {signed_supplier.name} for next season ({state.year + 1}) "
                f"as engine supplier, replacing {outgoing_supplier_name} on a {deal_type} deal."
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def get_player_replacement_candidates(self, state: GameState, outgoing_supplier_name: str) -> List[Any]:
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        if getattr(player_team, "builds_own_engine", False):
            raise ValueError("Self-built engine programmes cannot be replaced")
        if getattr(player_team, "engine_supplier_name", None) != outgoing_supplier_name:
            raise ValueError("Engine supplier is not assigned to the player team")

        outgoing_contract_length = int(getattr(player_team, "engine_supplier_contract_length", 0) or 0)
        if outgoing_contract_length >= 2:
            raise ValueError("Engine supplier has 2 or more years remaining on contract")

        return list(self._get_available_next_season_suppliers(state))

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
            if getattr(team, "builds_own_engine", False):
                continue
            contract_length = int(getattr(team, "engine_supplier_contract_length", 0) or 0)
            supplier_name = getattr(team, "engine_supplier_name", None)
            if not supplier_name or contract_length == 1:
                vacancies.append({"team_id": team.id, "team_name": team.name, "team": team})

        return vacancies

    def _get_available_next_season_suppliers(self, state: GameState) -> List[Any]:
        return [s for s in state.engine_suppliers if s.name != "Ferano"]

    def _pick_deal_for_team(self, team: Any) -> tuple[str, int]:
        team_speed = int(getattr(team, "car_speed", 50) or 50)
        if team_speed >= 80:
            deal_type = random.choices(
                ["works", "partner", "customer"],
                weights=[0.35, 0.4, 0.25],
                k=1,
            )[0]
        elif team_speed >= 60:
            deal_type = random.choices(
                ["works", "partner", "customer"],
                weights=[0.1, 0.45, 0.45],
                k=1,
            )[0]
        else:
            deal_type = random.choices(
                ["works", "partner", "customer"],
                weights=[0.03, 0.22, 0.75],
                k=1,
            )[0]

        yearly_cost = self.CUSTOMER_COST if deal_type == "customer" else 0
        return deal_type, yearly_cost
