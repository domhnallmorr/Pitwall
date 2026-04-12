import random
from typing import Any

from app.core.management_transfer_markets.title_sponsor import TitleSponsorTransferManager
from app.core.transfers import TransferManager
from app.models.email import EmailCategory
from app.models.state import GameState


class PlayerTitleSponsorNegotiationManager:
    def __init__(self):
        self.transfer_manager = TransferManager()
        self.title_sponsor_transfer_manager = TitleSponsorTransferManager()

    def get_market_payload(self, state: GameState) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        blocked_reason = self._blocked_reason(state, player_team)
        active = self._serialize_negotiation(state.player_title_sponsor_negotiation)
        sponsors = [
            {
                "id": sponsor.id,
                "name": sponsor.name,
                "wealth": sponsor.wealth,
                "targetable": blocked_reason is None and (active is None or active["sponsor_id"] == sponsor.id),
            }
            for sponsor in self._available_sponsors(state)
        ]
        commercial_manager = next(
            (manager for manager in state.commercial_managers if manager.id == getattr(player_team, "commercial_manager_id", None)),
            None,
        )
        return {
            "blocked_reason": blocked_reason,
            "current_sponsor_name": getattr(player_team, "title_sponsor_name", None),
            "commercial_staff_total": int(getattr(player_team, "commercial_staff", 0) or 0),
            "commercial_manager": {
                "name": commercial_manager.name if commercial_manager else "Unassigned",
                "skill": int(getattr(commercial_manager, "skill", 0) or 0),
            },
            "active_negotiation": active,
            "sponsors": sponsors,
        }

    def start_negotiation(self, state: GameState, sponsor_id: int) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        blocked_reason = self._blocked_reason(state, player_team)
        if blocked_reason:
            raise ValueError(blocked_reason)

        current = state.player_title_sponsor_negotiation
        if current is not None:
            if int(current.get("sponsor_id") or 0) != sponsor_id:
                raise ValueError("Only one title sponsor negotiation can be active at a time")
            return self._serialize_negotiation(current)

        sponsor = next((s for s in self._available_sponsors(state) if s.id == sponsor_id), None)
        if sponsor is None:
            raise ValueError("Selected title sponsor is not available for negotiation")

        negotiation = self._generate_negotiation(state, sponsor)
        state.player_title_sponsor_negotiation = negotiation
        state.add_email(
            sender="Commercial Department",
            subject=f"Title Sponsor Negotiation Opened: {sponsor.name}",
            body=(
                f"You have opened title sponsor negotiations with {sponsor.name}.\n\n"
                f"Assign commercial staff and build enough progress boxes to complete the deal."
            ),
            category=EmailCategory.SEASON,
        )
        return self._serialize_negotiation(negotiation)

    def update_assigned_staff(self, state: GameState, assigned_staff: int) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        negotiation = state.player_title_sponsor_negotiation
        if negotiation is None:
            raise ValueError("No active title sponsor negotiation")

        max_staff = int(getattr(player_team, "commercial_staff", 0) or 0)
        if assigned_staff < 0 or assigned_staff > max_staff:
            raise ValueError(f"Assigned staff must be between 0 and {max_staff}")

        negotiation["assigned_staff"] = assigned_staff
        return self._serialize_negotiation(negotiation)

    def progress_after_race(self, state: GameState) -> dict[str, Any] | None:
        negotiation = state.player_title_sponsor_negotiation
        if negotiation is None:
            return None

        before_boxes = int(negotiation.get("progress_boxes", 0) or 0)
        gain = self._progress_gain(state, negotiation)
        negotiation["progress"] = min(float(negotiation["total_boxes"]), float(negotiation.get("progress", 0.0) or 0.0) + gain)
        negotiation["progress_boxes"] = min(
            int(negotiation["total_boxes"]),
            int(float(negotiation["progress"]) // 1),
        )

        after_boxes = int(negotiation.get("progress_boxes", 0) or 0)
        event_name = state.calendar.current_event.name if state.calendar.current_event else "Grand Prix"
        if after_boxes > before_boxes:
            state.add_email(
                sender="Commercial Department",
                subject=f"Title Sponsor Negotiation Update: {negotiation['sponsor_name']}",
                body=(
                    f"Talks with {negotiation['sponsor_name']} moved forward after {event_name}.\n\n"
                    f"Progress: {after_boxes}/{negotiation['total_boxes']} boxes"
                ),
                category=EmailCategory.GENERAL,
            )
        return self._serialize_negotiation(negotiation)

    def sign_deal(self, state: GameState) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        blocked_reason = self._blocked_reason(state, player_team)
        if blocked_reason:
            raise ValueError(blocked_reason)

        negotiation = state.player_title_sponsor_negotiation
        if negotiation is None:
            raise ValueError("No active title sponsor negotiation")
        if int(negotiation.get("progress_boxes", 0) or 0) < int(negotiation.get("total_boxes", 0) or 0):
            raise ValueError("The title sponsor deal is not ready to sign yet")

        announced = list(state.announced_ai_title_sponsor_signings)
        existing = next((s for s in announced if s["team_id"] == player_team.id), None)
        if existing:
            announced.remove(existing)

        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": "title_sponsor_name",
            "seat_label": "Title Sponsor",
            "sponsor_id": negotiation["sponsor_id"],
            "sponsor_name": negotiation["sponsor_name"],
            "sponsor_wealth": int(negotiation["sponsor_wealth"]),
            "annual_value": int(negotiation["annual_value"]),
            "contract_length": int(negotiation["contract_length"]),
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player_negotiation",
        }
        announced.append(signing)
        state.announced_ai_title_sponsor_signings = announced
        state.player_title_sponsor_negotiation = None
        self.title_sponsor_transfer_manager.recompute_ai_signings(state)

        state.add_email(
            sender="Commercial Department",
            subject=f"Title Sponsor Signed: {signing['sponsor_name']}",
            body=(
                f"You have signed {signing['sponsor_name']} as title sponsor for next season ({state.year + 1}).\n\n"
                f"Annual value: ${signing['annual_value']:,}\n"
                f"Contract length: {signing['contract_length']} year(s)"
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def _require_player_team(self, state: GameState):
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        return player_team

    def _blocked_reason(self, state: GameState, player_team: Any) -> str | None:
        if int(getattr(player_team, "title_sponsor_contract_length", 0) or 0) >= 2:
            return "Current title sponsor has 2 or more years remaining on contract"
        if any(s.get("status") == "announced" and s.get("team_id") == player_team.id for s in state.announced_ai_title_sponsor_signings):
            return "A next-season title sponsor deal has already been agreed"
        return None

    def _available_sponsors(self, state: GameState) -> list[Any]:
        player_team = state.player_team
        current_name = getattr(player_team, "title_sponsor_name", None) if player_team else None
        blocked_ids = {s["sponsor_id"] for s in state.announced_ai_title_sponsor_signings if s["team_id"] != getattr(player_team, "id", None)}
        retained_names = {
            getattr(team, "title_sponsor_name", None)
            for team in state.teams
            if team.id != getattr(player_team, "id", None)
            and getattr(team, "title_sponsor_name", None)
            and int(getattr(team, "title_sponsor_contract_length", 0) or 0) > 1
        }
        return [
            sponsor
            for sponsor in state.title_sponsors
            if sponsor.start_year <= state.year
            and sponsor.id not in blocked_ids
            and sponsor.name not in retained_names
            and sponsor.name != current_name
        ]

    def _generate_negotiation(self, state: GameState, sponsor: Any) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        commercial_manager = next(
            (manager for manager in state.commercial_managers if manager.id == getattr(player_team, "commercial_manager_id", None)),
            None,
        )
        manager_skill = int(getattr(commercial_manager, "skill", 0) or 0)
        team_desirability = self.transfer_manager._team_desirability(state, player_team)  # noqa: SLF001
        team_strength = int(getattr(player_team, "car_speed", 50) or 50)
        sponsor_wealth = int(getattr(sponsor, "wealth", 0) or 0)
        team_score = team_desirability + int(round(manager_skill * 0.4)) + int(round(team_strength * 0.15))

        total_boxes = max(4, min(8, 4 + round((sponsor_wealth - team_score) / 18)))
        annual_value = max(
            2_500_000,
            int(round((sponsor_wealth * 310_000) + (team_desirability * 90_000) + max(team_strength - 60, 0) * 45_000)),
        )
        contract_length = 1 if sponsor_wealth < 45 else 2 if sponsor_wealth < 80 else 3

        return {
            "sponsor_id": sponsor.id,
            "sponsor_name": sponsor.name,
            "sponsor_wealth": sponsor_wealth,
            "assigned_staff": max(0, min(int(getattr(player_team, "commercial_staff", 0) or 0), 14)),
            "progress": 0.0,
            "progress_boxes": 0,
            "total_boxes": total_boxes,
            "annual_value": annual_value,
            "contract_length": contract_length,
            "started_year": state.year,
            "started_week": state.calendar.current_week,
            "status": "active",
        }

    def _serialize_negotiation(self, negotiation: dict[str, Any] | None) -> dict[str, Any] | None:
        if negotiation is None:
            return None
        progress = float(negotiation.get("progress", 0.0) or 0.0)
        total_boxes = int(negotiation.get("total_boxes", 0) or 0)
        progress_boxes = min(total_boxes, int(progress // 1))
        return {
            "sponsor_id": int(negotiation["sponsor_id"]),
            "sponsor_name": negotiation["sponsor_name"],
            "sponsor_wealth": int(negotiation.get("sponsor_wealth", 0) or 0),
            "assigned_staff": int(negotiation.get("assigned_staff", 0) or 0),
            "progress": progress,
            "progress_boxes": progress_boxes,
            "total_boxes": total_boxes,
            "annual_value": int(negotiation.get("annual_value", 0) or 0),
            "contract_length": int(negotiation.get("contract_length", 0) or 0),
            "started_year": int(negotiation.get("started_year", 0) or 0),
            "started_week": int(negotiation.get("started_week", 0) or 0),
            "status": negotiation.get("status", "active"),
            "ready_to_sign": progress_boxes >= total_boxes,
        }

    def _progress_gain(self, state: GameState, negotiation: dict[str, Any]) -> float:
        player_team = self._require_player_team(state)
        commercial_manager = next(
            (manager for manager in state.commercial_managers if manager.id == getattr(player_team, "commercial_manager_id", None)),
            None,
        )
        manager_skill = int(getattr(commercial_manager, "skill", 0) or 0)
        total_staff = max(1, int(getattr(player_team, "commercial_staff", 0) or 0))
        assigned_staff = max(0, int(negotiation.get("assigned_staff", 0) or 0))
        staff_ratio = assigned_staff / total_staff
        base = 0.3
        staff_component = staff_ratio * 1.15
        manager_component = manager_skill / 140
        difficulty_drag = int(negotiation.get("total_boxes", 0) or 0) / 70
        random_component = random.uniform(0.0, 0.35)
        return max(0.25, base + staff_component + manager_component + random_component - difficulty_drag)
