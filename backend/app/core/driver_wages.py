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
class DriverWageCharge:
    driver_name: str
    annual_wage: int
    races_in_season: int
    applied_amount: int
    event_name: str
    country: str


class DriverWageManager:
    def _count_races(self, state: GameState) -> int:
        return count_races(state)

    def calculate_race_wage(self, annual_wage: int, races_in_season: int) -> int:
        return int(round(annual_wage / max(1, races_in_season)))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> list[DriverWageCharge]:
        if not state.player_team:
            return []
        if not event_matches(event, [EventType.RACE]):
            return []

        races_in_season = self._count_races(state)
        context = resolve_event_charge_context(state, event)
        charges: list[DriverWageCharge] = []

        for driver in state.drivers:
            if driver.team_id != state.player_team_id:
                continue

            race_wage = self.calculate_race_wage(driver.wage, races_in_season)
            # Regular drivers have positive wage (expense); pay drivers are negative (income).
            amount = -race_wage
            if amount == 0:
                continue

            post_event_transaction(
                state,
                context,
                amount=amount,
                category=TransactionCategory.DRIVER_WAGES,
                description=f"Race wage: {driver.name}",
            )

            charges.append(
                DriverWageCharge(
                    driver_name=driver.name,
                    annual_wage=driver.wage,
                    races_in_season=races_in_season,
                    applied_amount=amount,
                    event_name=context.event_name,
                    country=context.country,
                )
            )

        return charges
