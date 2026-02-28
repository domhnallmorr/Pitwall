from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass
class FacilitiesUpgradePreview:
    requested_points: int
    effective_points: int
    years: int
    total_races: int
    total_cost: int
    per_race_payment: int
    current_facilities: int
    projected_facilities: int


@dataclass
class FacilitiesUpgradeCharge:
    event_name: str
    applied_cost: int
    remaining_cost: int
    races_paid: int
    total_races: int


class FacilitiesUpgradeManager:
    MIN_POINTS = 20
    MAX_POINTS = 40
    MIN_YEARS = 1
    MAX_YEARS = 3
    BASE_COST_AT_20 = 10_000_000
    COST_PER_POINT_ABOVE_20 = 750_000

    def _race_count(self, state: GameState) -> int:
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def _cost_for_points(self, points: int) -> int:
        clamped = max(self.MIN_POINTS, min(self.MAX_POINTS, points))
        return self.BASE_COST_AT_20 + ((clamped - self.MIN_POINTS) * self.COST_PER_POINT_ABOVE_20)

    def preview(self, state: GameState, points: int, years: int) -> FacilitiesUpgradePreview:
        player_team = state.player_team
        if not player_team:
            raise ValueError("No player team assigned")
        if years < self.MIN_YEARS or years > self.MAX_YEARS:
            raise ValueError(f"Repayment years must be between {self.MIN_YEARS} and {self.MAX_YEARS}")
        if points < self.MIN_POINTS or points > self.MAX_POINTS:
            raise ValueError(f"Upgrade value must be between {self.MIN_POINTS} and {self.MAX_POINTS}")

        current = max(0, int(player_team.facilities or 0))
        projected = min(100, current + points)
        effective_points = max(0, projected - current)
        total_cost = 0 if effective_points <= 0 else self._cost_for_points(effective_points)
        total_races = self._race_count(state) * years
        per_race = int(round(total_cost / max(1, total_races)))

        return FacilitiesUpgradePreview(
            requested_points=points,
            effective_points=effective_points,
            years=years,
            total_races=total_races,
            total_cost=total_cost,
            per_race_payment=per_race,
            current_facilities=current,
            projected_facilities=projected,
        )

    def start_upgrade(self, state: GameState, points: int, years: int) -> FacilitiesUpgradePreview:
        if state.finance.facilities_upgrade_active:
            raise ValueError("A facilities upgrade financing plan is already active")
        preview = self.preview(state, points, years)
        if preview.effective_points <= 0:
            raise ValueError("Facilities are already at maximum (100)")

        team = state.player_team
        team.facilities = preview.projected_facilities
        state.finance.facilities_upgrade_active = True
        state.finance.facilities_upgrade_total_cost = preview.total_cost
        state.finance.facilities_upgrade_paid = 0
        state.finance.facilities_upgrade_total_races = preview.total_races
        state.finance.facilities_upgrade_races_paid = 0
        state.finance.facilities_upgrade_years = years
        state.finance.facilities_upgrade_points = preview.effective_points

        state.add_email(
            sender="Infrastructure Department",
            subject=f"Facilities Upgrade Approved: +{preview.effective_points}",
            body=(
                f"Facilities upgrade has begun.\n\n"
                f"Old rating: {preview.current_facilities}\n"
                f"New rating: {preview.projected_facilities}\n"
                f"Total project cost: ${preview.total_cost:,}\n"
                f"Repayment period: {preview.years} year(s) ({preview.total_races} race installments)\n"
                f"Per-race payment: ${preview.per_race_payment:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return preview

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> Optional[FacilitiesUpgradeCharge]:
        if event is None or event.type != EventType.RACE:
            return None
        if not state.finance.facilities_upgrade_active:
            return None
        total = max(0, int(state.finance.facilities_upgrade_total_cost))
        paid = max(0, int(state.finance.facilities_upgrade_paid))
        remaining = max(0, total - paid)
        if remaining <= 0:
            state.finance.facilities_upgrade_active = False
            return None

        races_left = max(1, int(state.finance.facilities_upgrade_total_races) - int(state.finance.facilities_upgrade_races_paid))
        installment = int(round(remaining / races_left))
        installment = max(1, min(remaining, installment))

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-installment,
            category=TransactionCategory.FACILITIES,
            description="Facilities upgrade financing installment",
            event_name=event.name,
            event_type=event.type.value,
            circuit_country=(next((c.country for c in state.circuits if c.name == event.name), None) or "Unknown"),
        )
        state.finance.facilities_upgrade_paid += installment
        state.finance.facilities_upgrade_races_paid += 1
        remaining_after = max(0, state.finance.facilities_upgrade_total_cost - state.finance.facilities_upgrade_paid)
        if remaining_after <= 0:
            state.finance.facilities_upgrade_active = False
            state.add_email(
                sender="Infrastructure Department",
                subject="Facilities Upgrade Financing Complete",
                body="All facilities upgrade installments have been paid in full.",
                category=EmailCategory.GENERAL,
            )

        return FacilitiesUpgradeCharge(
            event_name=event.name,
            applied_cost=installment,
            remaining_cost=remaining_after,
            races_paid=state.finance.facilities_upgrade_races_paid,
            total_races=state.finance.facilities_upgrade_total_races,
        )
