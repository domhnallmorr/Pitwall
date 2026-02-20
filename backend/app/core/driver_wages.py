from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


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
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def calculate_race_wage(self, annual_wage: int, races_in_season: int) -> int:
        return int(round(annual_wage / max(1, races_in_season)))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> list[DriverWageCharge]:
        if not state.player_team:
            return []
        if event is None or event.type != EventType.RACE:
            return []

        races_in_season = self._count_races(state)
        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"
        charges: list[DriverWageCharge] = []

        for driver in state.drivers:
            if driver.team_id != state.player_team_id:
                continue

            race_wage = self.calculate_race_wage(driver.wage, races_in_season)
            # Regular drivers have positive wage (expense); pay drivers are negative (income).
            amount = -race_wage
            if amount == 0:
                continue

            state.finance.add_transaction(
                week=state.calendar.current_week,
                year=state.year,
                amount=amount,
                category=TransactionCategory.DRIVER_WAGES,
                description=f"Race wage: {driver.name}",
                event_name=event.name,
                event_type=event.type.value,
                circuit_country=country,
            )

            charges.append(
                DriverWageCharge(
                    driver_name=driver.name,
                    annual_wage=driver.wage,
                    races_in_season=races_in_season,
                    applied_amount=amount,
                    event_name=event.name,
                    country=country,
                )
            )

        return charges
