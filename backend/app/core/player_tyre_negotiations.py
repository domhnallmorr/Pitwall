import random
from typing import Any

from app.core.management_transfers import TyreSupplierTransferManager
from app.core.player_negotiation_hospitality import (
    apply_hospitality_charge,
    book_hospitality,
    get_hospitality_status,
    pop_hospitality_bonus,
)
from app.core.transfers import TransferManager
from app.models.email import EmailCategory
from app.models.state import GameState


class PlayerTyreNegotiationManager:
    CUSTOMER_COST = 450_000

    def __init__(self):
        self.transfer_manager = TransferManager()
        self.tyre_transfer_manager = TyreSupplierTransferManager()

    def get_market_payload(self, state: GameState) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        blocked_reason = self._blocked_reason(state, player_team)
        active = self._serialize_negotiation(state.player_tyre_negotiation)
        suppliers = [
            {
                "id": supplier.id,
                "name": supplier.name,
                "country": supplier.country,
                "resources": supplier.resources,
                "innovation": supplier.innovation,
                "reliability": supplier.reliability,
                "targetable": blocked_reason is None and (active is None or active["supplier_id"] == supplier.id),
            }
            for supplier in self._available_suppliers(state)
        ]
        commercial_manager = next(
            (manager for manager in state.commercial_managers if manager.id == getattr(player_team, "commercial_manager_id", None)),
            None,
        )
        return {
            "blocked_reason": blocked_reason,
            "current_supplier_name": getattr(player_team, "tyre_supplier_name", None),
            "commercial_staff_total": int(getattr(player_team, "commercial_staff", 0) or 0),
            "commercial_manager": {
                "name": commercial_manager.name if commercial_manager else "Unassigned",
                "skill": int(getattr(commercial_manager, "skill", 0) or 0),
            },
            "active_negotiation": active,
            "hospitality": get_hospitality_status(state, "tyre", active_negotiation=active is not None),
            "suppliers": suppliers,
        }

    def start_negotiation(self, state: GameState, supplier_id: int) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        blocked_reason = self._blocked_reason(state, player_team)
        if blocked_reason:
            raise ValueError(blocked_reason)

        current = state.player_tyre_negotiation
        if current is not None:
            if int(current.get("supplier_id") or 0) != supplier_id:
                raise ValueError("Only one tyre supplier negotiation can be active at a time")
            return self._serialize_negotiation(current)

        supplier = next((s for s in self._available_suppliers(state) if s.id == supplier_id), None)
        if supplier is None:
            raise ValueError("Selected tyre supplier is not available for negotiation")

        negotiation = self._generate_negotiation(state, supplier)
        state.player_tyre_negotiation = negotiation
        state.add_email(
            sender="Commercial Department",
            subject=f"Tyre Negotiation Opened: {supplier.name}",
            body=(
                f"You have opened tyre supplier negotiations with {supplier.name}.\n\n"
                f"Reach the marked thresholds to unlock Customer, Partner, or Works terms.\n"
                f"Assign commercial staff to speed up the talks."
            ),
            category=EmailCategory.SEASON,
        )
        return self._serialize_negotiation(negotiation)

    def update_assigned_staff(self, state: GameState, assigned_staff: int) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        negotiation = state.player_tyre_negotiation
        if negotiation is None:
            raise ValueError("No active tyre supplier negotiation")

        max_staff = int(getattr(player_team, "commercial_staff", 0) or 0)
        if assigned_staff < 0 or assigned_staff > max_staff:
            raise ValueError(f"Assigned staff must be between 0 and {max_staff}")

        negotiation["assigned_staff"] = assigned_staff
        return self._serialize_negotiation(negotiation)

    def progress_after_race(self, state: GameState) -> dict[str, Any] | None:
        negotiation = state.player_tyre_negotiation
        if negotiation is None:
            return None

        before_boxes = int(negotiation.get("progress_boxes", 0) or 0)
        before_unlocked = set(self._unlocked_tiers(negotiation))
        gain = self._progress_gain(state, negotiation)
        negotiation["progress"] = min(float(negotiation["total_boxes"]), float(negotiation.get("progress", 0.0) or 0.0) + gain)
        negotiation["progress_boxes"] = min(
            int(negotiation["total_boxes"]),
            int(float(negotiation["progress"]) // 1),
        )

        after_boxes = int(negotiation.get("progress_boxes", 0) or 0)
        after_unlocked = set(self._unlocked_tiers(negotiation))
        newly_unlocked = [tier for tier in ("customer", "partner", "works") if tier in after_unlocked and tier not in before_unlocked]
        event_name = state.calendar.current_event.name if state.calendar.current_event else "Grand Prix"

        if newly_unlocked:
            unlocked_labels = ", ".join(tier.title() for tier in newly_unlocked)
            state.add_email(
                sender="Commercial Department",
                subject=f"Tyre Negotiation Progress: {negotiation['supplier_name']}",
                body=(
                    f"Talks with {negotiation['supplier_name']} progressed after {event_name}.\n\n"
                    f"Newly unlocked terms: {unlocked_labels}\n"
                    f"Progress: {after_boxes}/{negotiation['total_boxes']} boxes"
                ),
                category=EmailCategory.SEASON,
            )
        elif after_boxes > before_boxes:
            state.add_email(
                sender="Commercial Department",
                subject=f"Tyre Negotiation Update: {negotiation['supplier_name']}",
                body=(
                    f"Talks with {negotiation['supplier_name']} moved forward after {event_name}.\n\n"
                    f"Progress: {after_boxes}/{negotiation['total_boxes']} boxes"
                ),
                category=EmailCategory.GENERAL,
            )

        return self._serialize_negotiation(negotiation)

    def sign_deal(self, state: GameState, tier: str) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        blocked_reason = self._blocked_reason(state, player_team)
        if blocked_reason:
            raise ValueError(blocked_reason)

        negotiation = state.player_tyre_negotiation
        if negotiation is None:
            raise ValueError("No active tyre supplier negotiation")
        tier_key = str(tier or "").lower()
        if tier_key not in {"customer", "partner", "works"}:
            raise ValueError("Negotiated tier must be customer, partner, or works")
        if tier_key not in set(self._unlocked_tiers(negotiation)):
            raise ValueError("That deal tier has not been unlocked yet")

        announced = list(state.announced_ai_tyre_supplier_signings)
        existing = next((s for s in announced if s["team_id"] == player_team.id), None)
        if existing:
            announced.remove(existing)

        signing = {
            "team_id": player_team.id,
            "team_name": player_team.name,
            "seat": "tyre_supplier_name",
            "seat_label": "Tyre Supplier",
            "supplier_id": negotiation["supplier_id"],
            "supplier_name": negotiation["supplier_name"],
            "deal_type": tier_key,
            "yearly_cost": int(negotiation["annual_values"][tier_key]),
            "contract_length": int(negotiation["contract_length"]),
            "announce_week": state.calendar.current_week,
            "announce_year": state.year,
            "status": "announced",
            "origin": "player_negotiation",
        }
        announced.append(signing)
        state.announced_ai_tyre_supplier_signings = announced
        state.player_tyre_negotiation = None
        self.tyre_transfer_manager.recompute_ai_signings(state)

        state.add_email(
            sender="Commercial Department",
            subject=f"Tyre Deal Signed: {signing['supplier_name']}",
            body=(
                f"You have signed a {tier_key.title()} tyre deal with {signing['supplier_name']} "
                f"for next season ({state.year + 1}).\n\n"
                f"Annual value: {'+' if signing['yearly_cost'] < 0 else '-'}${abs(signing['yearly_cost']):,}\n"
                f"Contract length: {signing['contract_length']} year(s)"
            ),
            category=EmailCategory.SEASON,
        )
        return signing

    def book_hospitality(self, state: GameState) -> dict[str, Any]:
        negotiation = state.player_tyre_negotiation
        if negotiation is None:
            raise ValueError("No active tyre supplier negotiation")
        book_hospitality(state, "tyre", target_name=str(negotiation["supplier_name"]))
        return self.get_market_payload(state)

    def apply_hospitality_bonus_after_race(self, state: GameState) -> dict[str, Any] | None:
        negotiation = state.player_tyre_negotiation
        if negotiation is None:
            return None

        pending = pop_hospitality_bonus(state, "tyre")
        if pending is None:
            return None
        apply_hospitality_charge(state, pending)

        before_unlocked = set(self._unlocked_tiers(negotiation))
        negotiation["progress"] = min(
            float(negotiation["total_boxes"]),
            float(negotiation.get("progress", 0.0) or 0.0) + float(pending["progress_bonus"]),
        )
        negotiation["progress_boxes"] = min(
            int(negotiation["total_boxes"]),
            int(float(negotiation["progress"]) // 1),
        )
        after_unlocked = set(self._unlocked_tiers(negotiation))
        unlocked_labels = ", ".join(
            tier.title() for tier in ("customer", "partner", "works") if tier in after_unlocked and tier not in before_unlocked
        )

        body_lines = [
            f"The hospitality programme for {pending['target_name']} at {state.calendar.current_event.name} helped move the talks forward.",
            "",
            f"Bonus applied: +{pending['progress_bonus']:.1f} boxes",
            f"Progress: {negotiation['progress_boxes']}/{negotiation['total_boxes']} boxes",
        ]
        if unlocked_labels:
            body_lines.extend(["", f"Newly unlocked terms: {unlocked_labels}"])
        state.add_email(
            sender="Commercial Department",
            subject=f"Hospitality Report: {pending['target_name']}",
            body="\n".join(body_lines),
            category=EmailCategory.GENERAL,
        )
        return self._serialize_negotiation(negotiation)

    def _require_player_team(self, state: GameState):
        player_team = state.player_team
        if player_team is None:
            raise ValueError("No player team assigned")
        return player_team

    def _blocked_reason(self, state: GameState, player_team: Any) -> str | None:
        if int(getattr(player_team, "tyre_supplier_contract_length", 0) or 0) >= 2:
            return "Current tyre supplier has 2 or more years remaining on contract"
        if any(s.get("status") == "announced" and s.get("team_id") == player_team.id for s in state.announced_ai_tyre_supplier_signings):
            return "A next-season tyre supplier deal has already been agreed"
        return None

    def _available_suppliers(self, state: GameState) -> list[Any]:
        player_team = state.player_team
        current_name = getattr(player_team, "tyre_supplier_name", None) if player_team else None
        return [
            supplier for supplier in state.tyre_suppliers
            if supplier.start_year <= state.year and supplier.name != current_name
        ]

    def _generate_negotiation(self, state: GameState, supplier: Any) -> dict[str, Any]:
        player_team = self._require_player_team(state)
        commercial_manager = next(
            (manager for manager in state.commercial_managers if manager.id == getattr(player_team, "commercial_manager_id", None)),
            None,
        )
        manager_skill = int(getattr(commercial_manager, "skill", 0) or 0)
        team_desirability = self.transfer_manager._team_desirability(state, player_team)  # noqa: SLF001
        team_strength = int(getattr(player_team, "car_speed", 50) or 50)
        supplier_score = int(round((
            int(getattr(supplier, "resources", 0) or 0)
            + int(getattr(supplier, "innovation", 0) or 0)
            + int(getattr(supplier, "reliability", 0) or 0)
        ) / 3))
        team_score = team_desirability + int(round(manager_skill * 0.35)) + int(round(team_strength * 0.2))

        total_boxes = max(3, min(8, 4 + round((supplier_score - team_score) / 16)))
        customer_threshold = max(1, min(total_boxes, round(total_boxes * 0.35)))
        partner_available = team_score + supplier_score >= 120
        works_available = partner_available and team_strength >= 65 and team_score + supplier_score >= 150
        partner_threshold = max(customer_threshold + 1, min(total_boxes - 1, round(total_boxes * 0.68))) if partner_available and total_boxes >= 3 else None
        works_threshold = total_boxes if works_available else None

        available_tiers = ["customer"]
        if partner_available:
            available_tiers.append("partner")
        if works_available:
            available_tiers.append("works")

        contract_length = 2 if "works" in available_tiers else 1 if supplier_score < 82 else 2

        return {
            "supplier_id": supplier.id,
            "supplier_name": supplier.name,
            "assigned_staff": max(0, min(int(getattr(player_team, "commercial_staff", 0) or 0), 12)),
            "progress": 0.0,
            "progress_boxes": 0,
            "total_boxes": total_boxes,
            "customer_threshold": customer_threshold,
            "partner_threshold": partner_threshold,
            "works_threshold": works_threshold,
            "available_tiers": available_tiers,
            "annual_values": {
                "customer": self.CUSTOMER_COST,
                "partner": 0,
                "works": 0,
            },
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
            "supplier_id": int(negotiation["supplier_id"]),
            "supplier_name": negotiation["supplier_name"],
            "assigned_staff": int(negotiation.get("assigned_staff", 0) or 0),
            "progress": progress,
            "progress_boxes": progress_boxes,
            "total_boxes": total_boxes,
            "customer_threshold": int(negotiation.get("customer_threshold", 0) or 0),
            "partner_threshold": negotiation.get("partner_threshold"),
            "works_threshold": negotiation.get("works_threshold"),
            "available_tiers": list(negotiation.get("available_tiers", [])),
            "annual_values": dict(negotiation.get("annual_values", {})),
            "contract_length": int(negotiation.get("contract_length", 0) or 0),
            "started_year": int(negotiation.get("started_year", 0) or 0),
            "started_week": int(negotiation.get("started_week", 0) or 0),
            "status": negotiation.get("status", "active"),
            "unlocked_tiers": self._unlocked_tiers(negotiation),
        }

    def _unlocked_tiers(self, negotiation: dict[str, Any]) -> list[str]:
        progress_boxes = int(negotiation.get("progress_boxes", int(float(negotiation.get("progress", 0.0) or 0.0) // 1)) or 0)
        unlocked = []
        if progress_boxes >= int(negotiation.get("customer_threshold", 0) or 0):
            unlocked.append("customer")
        partner_threshold = negotiation.get("partner_threshold")
        if partner_threshold is not None and progress_boxes >= int(partner_threshold):
            unlocked.append("partner")
        works_threshold = negotiation.get("works_threshold")
        if works_threshold is not None and progress_boxes >= int(works_threshold):
            unlocked.append("works")
        return unlocked

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
        base = 0.25
        staff_component = staff_ratio * 1.05
        manager_component = manager_skill / 155
        supplier_drag = ((int(negotiation.get("works_threshold") or 0) > 0) * 0.06) + (int(negotiation.get("total_boxes", 0) or 0) / 65)
        random_component = random.uniform(0.0, 0.35)
        return max(0.2, base + staff_component + manager_component + random_component - supplier_drag)
