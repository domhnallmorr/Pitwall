from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass
class SponsorshipCharge:
    event_name: str
    country: str
    sponsor_name: str
    yearly_value: int
    races_in_season: int
    applied_income: int


class SponsorshipManager:
    def _count_races(self, state: GameState) -> int:
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def calculate_race_installment(self, yearly_value: int, races_in_season: int) -> int:
        return max(0, int(round(max(0, yearly_value) / max(1, races_in_season))))

    def apply_for_event(self, state: GameState, event: Optional[Event]) -> Optional[SponsorshipCharge]:
        team = state.player_team
        if not team:
            return None
        if event is None or event.type != EventType.RACE:
            return None

        sponsor_name = team.title_sponsor_name
        yearly_value = team.title_sponsor_yearly
        if not sponsor_name or yearly_value <= 0:
            return None

        races_in_season = self._count_races(state)
        installment = self.calculate_race_installment(yearly_value, races_in_season)
        if installment <= 0:
            return None

        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=installment,
            category=TransactionCategory.SPONSORSHIP,
            description=f"Title sponsor installment: {sponsor_name}",
            event_name=event.name,
            event_type=event.type.value,
            circuit_country=country,
        )

        return SponsorshipCharge(
            event_name=event.name,
            country=country,
            sponsor_name=sponsor_name,
            yearly_value=yearly_value,
            races_in_season=races_in_season,
            applied_income=installment,
        )
