from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.core.finance_event_charges import (
    count_races,
    event_matches,
    post_event_transaction,
    resolve_event_charge_context,
)


@dataclass
class OperationalStaffCharge:
    label: str
    annual_avg_wage: int
    staff_count: int
    races_in_season: int
    applied_cost: int
    category: TransactionCategory


@dataclass
class OperationalStaffChargeBatch:
    event_name: str
    country: str
    charges: list[OperationalStaffCharge]

    @property
    def total_cost(self) -> int:
        return sum(charge.applied_cost for charge in self.charges)

    @property
    def total_staff(self) -> int:
        return sum(charge.staff_count for charge in self.charges)


class OperationalStaffCostManager:
    def __init__(
        self,
        design_annual_avg_wage: int = 25_000,
        engineering_annual_avg_wage: int = 22_000,
        mechanics_annual_avg_wage: int = 20_000,
    ):
        self.design_annual_avg_wage = design_annual_avg_wage
        self.engineering_annual_avg_wage = engineering_annual_avg_wage
        self.mechanics_annual_avg_wage = mechanics_annual_avg_wage

    def _count_races(self, state: GameState) -> int:
        return count_races(state)

    def calculate_race_cost(self, staff_count: int, annual_avg_wage: int, races_in_season: int) -> int:
        return max(0, int(round((max(0, staff_count) * annual_avg_wage) / max(1, races_in_season))))

    def calculate_department_race_costs(self, team, races_in_season: int) -> dict[str, int]:
        design_staff = int(getattr(team, "design_staff", 0) or 0)
        engineering_staff = int(getattr(team, "engineering_staff", 0) or 0)
        mechanics_staff = int(getattr(team, "mechanics_staff", 0) or 0)
        return {
            "design": self.calculate_race_cost(design_staff, self.design_annual_avg_wage, races_in_season),
            "engineering": self.calculate_race_cost(engineering_staff, self.engineering_annual_avg_wage, races_in_season),
            "mechanics": self.calculate_race_cost(mechanics_staff, self.mechanics_annual_avg_wage, races_in_season),
        }

    def calculate_total_race_cost(self, team, races_in_season: int) -> int:
        costs = self.calculate_department_race_costs(team, races_in_season)
        return sum(costs.values())

    def calculate_total_annual_cost(self, team) -> int:
        return (
            max(0, int(getattr(team, "design_staff", 0) or 0)) * self.design_annual_avg_wage
            + max(0, int(getattr(team, "engineering_staff", 0) or 0)) * self.engineering_annual_avg_wage
            + max(0, int(getattr(team, "mechanics_staff", 0) or 0)) * self.mechanics_annual_avg_wage
        )

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> Optional[OperationalStaffChargeBatch]:
        if not state.player_team:
            return None
        if not event_matches(event, [EventType.RACE]):
            return None

        team = state.player_team
        races_in_season = self._count_races(state)
        context = resolve_event_charge_context(state, event)

        charge_specs = [
            (
                "Design",
                int(getattr(team, "design_staff", 0) or 0),
                self.design_annual_avg_wage,
                TransactionCategory.DESIGN_STAFF_WAGES,
            ),
            (
                "Engineering",
                int(getattr(team, "engineering_staff", 0) or 0),
                self.engineering_annual_avg_wage,
                TransactionCategory.ENGINEERING_STAFF_WAGES,
            ),
            (
                "Mechanics",
                int(getattr(team, "mechanics_staff", 0) or 0),
                self.mechanics_annual_avg_wage,
                TransactionCategory.MECHANICS_STAFF_WAGES,
            ),
        ]

        applied_charges: list[OperationalStaffCharge] = []
        for label, staff_count, annual_avg_wage, category in charge_specs:
            applied_cost = self.calculate_race_cost(staff_count, annual_avg_wage, races_in_season)
            if applied_cost <= 0:
                continue
            post_event_transaction(
                state,
                context,
                amount=-applied_cost,
                category=category,
                description=f"Race {label.lower()} staff payroll ({staff_count} staff)",
            )
            applied_charges.append(
                OperationalStaffCharge(
                    label=label,
                    annual_avg_wage=annual_avg_wage,
                    staff_count=staff_count,
                    races_in_season=races_in_season,
                    applied_cost=applied_cost,
                    category=category,
                )
            )

        if not applied_charges:
            return None

        return OperationalStaffChargeBatch(
            event_name=context.event_name,
            country=context.country,
            charges=applied_charges,
        )
