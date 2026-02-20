import random
from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass(frozen=True)
class DamageTier:
    label: str
    min_cost: int
    max_cost: int
    probability: float


DAMAGE_TIERS = (
    DamageTier("minor", 50_000, 150_000, 0.5),
    DamageTier("moderate", 150_000, 300_000, 0.3),
    DamageTier("severe", 300_000, 450_000, 0.15),
    DamageTier("very severe", 450_000, 500_000, 0.05),
)


@dataclass
class CrashDamageCharge:
    driver_name: str
    tier: str
    applied_cost: int
    event_name: str
    country: str


class CrashDamageManager:
    def pick_tier(self, rng: Optional[random.Random] = None) -> DamageTier:
        random_source = rng if rng is not None else random
        roll = random_source.random()
        cumulative = 0.0
        for tier in DAMAGE_TIERS:
            cumulative += tier.probability
            if roll <= cumulative:
                return tier
        return DAMAGE_TIERS[-1]

    def calculate_damage_cost(self, rng: Optional[random.Random] = None) -> tuple[DamageTier, int]:
        random_source = rng if rng is not None else random
        tier = self.pick_tier(random_source)
        cost = random_source.randint(tier.min_cost, tier.max_cost)
        return tier, cost

    def charge_for_race(
        self,
        state: GameState,
        race_result: dict,
        event: Optional[Event],
        rng: Optional[random.Random] = None,
    ) -> list[CrashDamageCharge]:
        if not state.player_team:
            return []
        if event is None or event.type != EventType.RACE:
            return []

        crash_outs = race_result.get("crash_outs", [])
        player_crash_outs = [c for c in crash_outs if c.get("team_id") == state.player_team_id]
        if not player_crash_outs:
            return []

        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"
        charges: list[CrashDamageCharge] = []

        for crash in player_crash_outs:
            driver_name = crash.get("driver_name", "Unknown Driver")
            tier, applied_cost = self.calculate_damage_cost(rng=rng)
            state.finance.add_transaction(
                week=state.calendar.current_week,
                year=state.year,
                amount=-applied_cost,
                category=TransactionCategory.CRASH_DAMAGE,
                description=f"Crash repairs for {driver_name} ({tier.label})",
                event_name=event.name,
                event_type=event.type.value,
                circuit_country=country,
            )
            charges.append(
                CrashDamageCharge(
                    driver_name=driver_name,
                    tier=tier.label,
                    applied_cost=applied_cost,
                    event_name=event.name,
                    country=country,
                )
            )

        return charges
