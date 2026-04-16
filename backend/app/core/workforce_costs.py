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
class WorkforceCharge:
    event_name: str
    country: str
    annual_avg_wage: int
    workforce: int
    races_in_season: int
    applied_cost: int


class WorkforceCostManager:
    def __init__(self, annual_avg_wage: int = 28_000):
        self.annual_avg_wage = annual_avg_wage

    def _count_races(self, state: GameState) -> int:
        return count_races(state)

    def calculate_race_cost(self, workforce: int, races_in_season: int) -> int:
        return max(0, int(round((max(0, workforce) * self.annual_avg_wage) / max(1, races_in_season))))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> Optional[WorkforceCharge]:
        if not state.player_team:
            return None
        if not event_matches(event, [EventType.RACE]):
            return None

        workforce = getattr(state.player_team, "workforce", 0) or 0
        races_in_season = self._count_races(state)
        applied_cost = self.calculate_race_cost(workforce, races_in_season)
        if applied_cost <= 0:
            return None

        context = resolve_event_charge_context(state, event)
        post_event_transaction(
            state,
            context,
            amount=-applied_cost,
            category=TransactionCategory.WORKFORCE_WAGES,
            description=f"Race workforce payroll ({workforce} staff)",
        )

        return WorkforceCharge(
            event_name=context.event_name,
            country=context.country,
            annual_avg_wage=self.annual_avg_wage,
            workforce=workforce,
            races_in_season=races_in_season,
            applied_cost=applied_cost,
        )
