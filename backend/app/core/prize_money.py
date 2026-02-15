from app.models.state import GameState
from app.models.finance import TransactionCategory
from app.models.calendar import EventType
from app.core.standings import StandingsManager


# 1998 constructor prize money table by finishing position.
PRIZE_MONEY_BY_POSITION = [
    33_000_000,
    31_000_000,
    27_000_000,
    23_000_000,
    13_000_000,
    11_000_000,
    9_000_000,
    7_000_000,
    5_000_000,
    3_000_000,
    1_000_000,
]


class PrizeMoneyManager:
    def assign_initial_entitlement_from_roster_order(self, state: GameState) -> dict:
        """Set season entitlement using roster team order (1997 finishing order)."""
        player_team = state.player_team
        if not player_team:
            return {"position": None, "entitlement": 0}

        position = next((i for i, t in enumerate(state.teams, start=1) if t.id == player_team.id), None)
        entitlement = self._get_entitlement_for_position(position)
        self._set_season_entitlement(state, entitlement)
        return {"position": position, "entitlement": entitlement}

    def assign_next_season_entitlement_from_standings(self, state: GameState) -> dict:
        """Set next season entitlement from end-of-season constructor standings."""
        player_team = state.player_team
        if not player_team:
            return {"position": None, "entitlement": 0}

        standings = StandingsManager().get_constructor_standings(state)
        position = next((i for i, t in enumerate(standings, start=1) if t.id == player_team.id), None)
        entitlement = self._get_entitlement_for_position(position)
        self._set_season_entitlement(state, entitlement)
        return {"position": position, "entitlement": entitlement}

    def process_race_payout(self, state: GameState) -> dict | None:
        """Pay prize money installment after a race."""
        player_team = state.player_team
        if not player_team:
            return None

        finance = state.finance
        total_races = finance.prize_money_total_races or self._count_races(state)
        if total_races <= 0:
            return None
        if finance.prize_money_races_paid >= total_races:
            return None

        base = finance.prize_money_entitlement // total_races
        remainder = finance.prize_money_entitlement % total_races
        installment = base + remainder if finance.prize_money_races_paid == 0 else base

        finance.prize_money_races_paid += 1
        finance.prize_money_paid += installment

        if installment > 0:
            state.finance.add_transaction(
                week=state.calendar.current_week,
                year=state.year,
                amount=installment,
                category=TransactionCategory.PRIZE_MONEY,
                description=f"Prize money installment ({finance.prize_money_races_paid}/{total_races})",
            )

        return {
            "installment": installment,
            "races_paid": finance.prize_money_races_paid,
            "total_races": total_races,
            "entitlement": finance.prize_money_entitlement,
        }

    def _set_season_entitlement(self, state: GameState, entitlement: int):
        state.finance.prize_money_entitlement = entitlement
        state.finance.prize_money_paid = 0
        state.finance.prize_money_races_paid = 0
        state.finance.prize_money_total_races = self._count_races(state)

    def _count_races(self, state: GameState) -> int:
        return sum(1 for e in state.calendar.events if e.type == EventType.RACE)

    def _get_entitlement_for_position(self, position: int | None) -> int:
        if not position or position < 1:
            return 0
        idx = position - 1
        if idx >= len(PRIZE_MONEY_BY_POSITION):
            return 0
        return PRIZE_MONEY_BY_POSITION[idx]
