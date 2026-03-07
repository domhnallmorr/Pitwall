from app.core.finance_reporting import build_finance_report
from app.core.sponsorships import SponsorshipManager
from app.models.finance import TransactionCategory
from app.models.state import GameState


def build_finance_payload(state: GameState):
    transactions = [t.model_dump() for t in state.finance.transactions]
    report = build_finance_report(state)
    player_team = state.player_team
    sponsor_name = player_team.title_sponsor_name if player_team else None
    sponsor_yearly = player_team.title_sponsor_yearly if player_team else 0
    other_sponsorship_yearly = player_team.other_sponsorship_yearly if player_team else 0
    race_count = state.finance.prize_money_total_races or max(
        1, sum(1 for e in state.calendar.events if getattr(e.type, "value", e.type) == "RACE")
    )
    sponsor_installment = SponsorshipManager().calculate_race_installment(
        sponsor_yearly, race_count
    ) if sponsor_name else 0
    other_sponsorship_installment = SponsorshipManager().calculate_race_installment(
        other_sponsorship_yearly, race_count
    ) if other_sponsorship_yearly > 0 else 0
    sponsor_paid_so_far = sum(
        t.amount for t in state.finance.transactions
        if (
            t.category == TransactionCategory.SPONSORSHIP
            and t.year == state.year
            and t.amount > 0
            and str(t.description).startswith("Title sponsor installment:")
        )
    )
    other_sponsorship_paid_so_far = sum(
        t.amount for t in state.finance.transactions
        if (
            t.category == TransactionCategory.SPONSORSHIP
            and t.year == state.year
            and t.amount > 0
            and str(t.description).startswith("Other sponsorship installment")
        )
    )
    sponsor_remaining = max(sponsor_yearly - sponsor_paid_so_far, 0) if sponsor_name else 0
    other_sponsorship_remaining = max(other_sponsorship_yearly - other_sponsorship_paid_so_far, 0)

    engine_supplier_name = player_team.engine_supplier_name if player_team else None
    engine_supplier_yearly = player_team.engine_supplier_yearly_cost if player_team else 0
    engine_supplier_installment = int(round(max(0, engine_supplier_yearly) / max(1, race_count))) if engine_supplier_name else 0
    engine_supplier_paid_so_far = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.ENGINE_SUPPLIER and t.year == state.year and t.amount < 0
    )
    engine_supplier_remaining = max(engine_supplier_yearly - engine_supplier_paid_so_far, 0) if engine_supplier_name else 0

    tyre_supplier_name = player_team.tyre_supplier_name if player_team else None
    tyre_supplier_yearly = player_team.tyre_supplier_yearly_cost if player_team else 0
    tyre_supplier_installment = int(round(max(0, tyre_supplier_yearly) / max(1, race_count))) if tyre_supplier_name else 0
    tyre_supplier_paid_so_far = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.TYRE_SUPPLIER and t.year == state.year and t.amount < 0
    )
    tyre_supplier_remaining = max(tyre_supplier_yearly - tyre_supplier_paid_so_far, 0) if tyre_supplier_name else 0
    facilities_upgrade_paid = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.FACILITIES and t.amount < 0
    )

    return {
        "balance": state.finance.balance,
        "prize_money_entitlement": state.finance.prize_money_entitlement,
        "prize_money_paid": state.finance.prize_money_paid,
        "prize_money_remaining": max(state.finance.prize_money_entitlement - state.finance.prize_money_paid, 0),
        "prize_money_races_paid": state.finance.prize_money_races_paid,
        "prize_money_total_races": state.finance.prize_money_total_races,
        "transactions": transactions,
        "summary": report["summary"],
        "track_profit_loss": report["track_profit_loss"],
        "sponsor": {
            "name": sponsor_name,
            "annual_value": sponsor_yearly,
            "installment": sponsor_installment,
            "paid_so_far": sponsor_paid_so_far,
            "remaining": sponsor_remaining,
        },
        "other_sponsorship": {
            "annual_value": other_sponsorship_yearly,
            "installment": other_sponsorship_installment,
            "paid_so_far": other_sponsorship_paid_so_far,
            "remaining": other_sponsorship_remaining,
        },
        "engine_supplier": {
            "name": engine_supplier_name,
            "deal": player_team.engine_supplier_deal if player_team else None,
            "annual_value": engine_supplier_yearly,
            "installment": engine_supplier_installment,
            "paid_so_far": engine_supplier_paid_so_far,
            "remaining": engine_supplier_remaining,
        },
        "tyre_supplier": {
            "name": tyre_supplier_name,
            "deal": player_team.tyre_supplier_deal if player_team else None,
            "annual_value": tyre_supplier_yearly,
            "installment": tyre_supplier_installment,
            "paid_so_far": tyre_supplier_paid_so_far,
            "remaining": tyre_supplier_remaining,
        },
        "facilities_upgrade": {
            "active": state.finance.facilities_upgrade_active,
            "total_cost": state.finance.facilities_upgrade_total_cost,
            "paid_so_far": state.finance.facilities_upgrade_paid,
            "remaining": max(state.finance.facilities_upgrade_total_cost - state.finance.facilities_upgrade_paid, 0),
            "races_paid": state.finance.facilities_upgrade_races_paid,
            "total_races": state.finance.facilities_upgrade_total_races,
            "years": state.finance.facilities_upgrade_years,
            "points": state.finance.facilities_upgrade_points,
            "historical_paid_total": facilities_upgrade_paid,
        },
    }
