from app.core.finance_reporting import build_finance_report
from app.core.sponsorships import SponsorshipManager
from app.core.transport import COUNTRY_COST_TIER, TransportCosts
from app.core.workforce_costs import WorkforceCostManager
from app.models.calendar import EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


def _find_circuit_country(state: GameState, event_name: str) -> str:
    circuit = next((c for c in state.circuits if c.name == event_name), None)
    return circuit.country if circuit else "Unknown"


def build_finance_payload(state: GameState):
    transactions = [t.model_dump() for t in state.finance.transactions]
    report = build_finance_report(state)
    player_team = state.player_team
    sponsor_name = player_team.title_sponsor_name if player_team else None
    sponsor_yearly = player_team.title_sponsor_yearly if player_team else 0
    sponsor_pending_replacement = any(
        s.get("status") == "announced" and s.get("team_id") == player_team.id
        for s in state.announced_ai_title_sponsor_signings
    ) if player_team else False
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
    workforce_manager = WorkforceCostManager()
    workforce_race_cost = workforce_manager.calculate_race_cost(player_team.workforce, race_count) if player_team else 0
    workforce_annual_projection = max(0, int(getattr(player_team, "workforce", 0) or 0)) * workforce_manager.annual_avg_wage if player_team else 0

    engine_supplier_name = player_team.engine_supplier_name if player_team else None
    engine_supplier_yearly = player_team.engine_supplier_yearly_cost if player_team else 0
    engine_supplier_pending_replacement = any(
        s.get("status") == "announced" and s.get("team_id") == player_team.id
        for s in state.announced_ai_engine_supplier_signings
    ) if player_team else False
    engine_supplier_installment = int(round(max(0, engine_supplier_yearly) / max(1, race_count))) if engine_supplier_name else 0
    engine_supplier_paid_so_far = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.ENGINE_SUPPLIER and t.year == state.year and t.amount < 0
    )
    engine_supplier_remaining = max(engine_supplier_yearly - engine_supplier_paid_so_far, 0) if engine_supplier_name else 0

    tyre_supplier_name = player_team.tyre_supplier_name if player_team else None
    tyre_supplier_yearly = player_team.tyre_supplier_yearly_cost if player_team else 0
    tyre_supplier_pending_replacement = any(
        s.get("status") == "announced" and s.get("team_id") == player_team.id
        for s in state.announced_ai_tyre_supplier_signings
    ) if player_team else False
    tyre_supplier_installment = int(round(max(0, tyre_supplier_yearly) / max(1, race_count))) if tyre_supplier_name else 0
    tyre_supplier_paid_so_far = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.TYRE_SUPPLIER and t.year == state.year and t.amount < 0
    )
    tyre_supplier_remaining = max(tyre_supplier_yearly - tyre_supplier_paid_so_far, 0) if tyre_supplier_name else 0

    fuel_supplier_name = player_team.fuel_supplier_name if player_team else None
    fuel_supplier_yearly = player_team.fuel_supplier_yearly_cost if player_team else 0
    fuel_supplier_installment = int(round(abs(fuel_supplier_yearly) / max(1, race_count))) if fuel_supplier_name else 0
    fuel_supplier_paid_so_far = sum(
        abs(t.amount) for t in state.finance.transactions
        if t.category == TransactionCategory.FUEL_SUPPLIER and t.year == state.year
    )
    fuel_supplier_remaining = max(abs(fuel_supplier_yearly) - fuel_supplier_paid_so_far, 0) if fuel_supplier_name else 0
    facilities_upgrade_paid = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.FACILITIES and t.amount < 0
    )
    facilities_remaining = max(state.finance.facilities_upgrade_total_cost - state.finance.facilities_upgrade_paid, 0)
    facilities_installment = int(round(state.finance.facilities_upgrade_total_cost / max(1, state.finance.facilities_upgrade_total_races))) if state.finance.facilities_upgrade_active and state.finance.facilities_upgrade_total_races else 0
    remaining_races = max(race_count - int(state.finance.prize_money_races_paid or 0), 0)

    summary = report["summary"]
    driver_wages_paid_so_far = sum(
        -t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.DRIVER_WAGES and t.year == state.year and t.amount < 0
    )
    driver_wages_received_so_far = sum(
        t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.DRIVER_WAGES and t.year == state.year and t.amount > 0
    )
    projected_driver_expense_remaining = max(
        sum(max(0, int(getattr(driver, "wage", 0) or 0)) for driver in state.drivers if driver.team_id == state.player_team_id)
        - driver_wages_paid_so_far,
        0,
    )
    projected_driver_income_remaining = max(
        sum(max(0, abs(int(getattr(driver, "wage", 0) or 0))) for driver in state.drivers if driver.team_id == state.player_team_id and int(getattr(driver, "wage", 0) or 0) < 0)
        - driver_wages_received_so_far,
        0,
    )
    projected_workforce_remaining = max(workforce_annual_projection - int(summary.get("workforce_total", 0) or 0), 0)
    prize_remaining = max(state.finance.prize_money_entitlement - state.finance.prize_money_paid, 0)
    next_race_prize_income = int(round(prize_remaining / max(1, remaining_races))) if remaining_races else 0
    transport_events_remaining = []
    for event in state.calendar.events:
        if event.week < state.calendar.current_week:
            continue
        if event.type not in {EventType.RACE, EventType.TEST}:
            continue
        already_charged = any(
            t.year == state.year
            and t.category == TransactionCategory.TRANSPORT
            and t.event_name == event.name
            for t in state.finance.transactions
        )
        if not already_charged:
            transport_events_remaining.append(event)

    projected_transport_remaining = sum(
        COUNTRY_COST_TIER.get(_find_circuit_country(state, event.name), TransportCosts.MEDIUM)
        for event in transport_events_remaining
    )

    next_race_event = next(
        (
            event for event in state.calendar.events
            if event.week >= state.calendar.current_week and event.type == EventType.RACE
            and not any(
                t.year == state.year
                and t.category == TransactionCategory.TRANSPORT
                and t.event_name == event.name
                for t in state.finance.transactions
            )
        ),
        None,
    )
    next_race_transport = 0
    next_race_driver_income = 0
    next_race_driver_cost = 0
    if next_race_event is not None:
        next_race_transport = COUNTRY_COST_TIER.get(_find_circuit_country(state, next_race_event.name), TransportCosts.MEDIUM)
        for driver in state.drivers:
            if driver.team_id != state.player_team_id:
                continue
            race_wage = int(round(abs(int(getattr(driver, "wage", 0) or 0)) / max(1, race_count)))
            if int(getattr(driver, "wage", 0) or 0) < 0:
                next_race_driver_income += race_wage
            else:
                next_race_driver_cost += race_wage

    next_race_income = sponsor_installment + other_sponsorship_installment + next_race_prize_income
    next_race_income += next_race_driver_income
    if fuel_supplier_yearly < 0:
        next_race_income += fuel_supplier_installment

    next_race_outgoings = (
        workforce_race_cost
        + engine_supplier_installment
        + tyre_supplier_installment
        + facilities_installment
        + next_race_transport
        + next_race_driver_cost
    )
    if fuel_supplier_yearly > 0:
        next_race_outgoings += fuel_supplier_installment
    next_race_net = next_race_income - next_race_outgoings

    projected_end_balance = state.finance.balance + prize_remaining + sponsor_remaining + other_sponsorship_remaining
    projected_end_balance += projected_driver_income_remaining
    projected_end_balance -= (
        engine_supplier_remaining
        + tyre_supplier_remaining
        + projected_workforce_remaining
        + projected_driver_expense_remaining
        + projected_transport_remaining
        + facilities_remaining
    )
    if fuel_supplier_yearly < 0:
        projected_end_balance += fuel_supplier_remaining
    else:
        projected_end_balance -= fuel_supplier_remaining

    contract_alerts = []
    if sponsor_name and int(getattr(player_team, "title_sponsor_contract_length", 0) or 0) <= 1:
        contract_alerts.append("Title sponsor deal expires after this season.")
    if engine_supplier_name:
        if bool(getattr(player_team, "builds_own_engine", False)):
            contract_alerts.append("Engine programme is locked in-house.")
        elif int(getattr(player_team, "engine_supplier_contract_length", 0) or 0) <= 1:
            contract_alerts.append("Engine supplier deal expires after this season.")
    if tyre_supplier_name and int(getattr(player_team, "tyre_supplier_contract_length", 0) or 0) <= 1:
        contract_alerts.append("Tyre supplier deal expires after this season.")
    if state.finance.facilities_upgrade_active and facilities_remaining > 0:
        contract_alerts.append(
            f"Facilities financing has {max(int(state.finance.facilities_upgrade_total_races or 0) - int(state.finance.facilities_upgrade_races_paid or 0), 0)} installments left."
        )
    if not contract_alerts:
        contract_alerts.append("No immediate contract risks.")

    if remaining_races > 0:
        prize_outlook = (
            f"${prize_remaining:,} of constructor prize money remains to be paid "
            f"across {remaining_races} race weekends."
        )
    else:
        prize_outlook = "All constructor prize installments have been paid for this season."

    return {
        "balance": state.finance.balance,
        "prize_money_entitlement": state.finance.prize_money_entitlement,
        "prize_money_paid": state.finance.prize_money_paid,
        "prize_money_remaining": prize_remaining,
        "prize_money_races_paid": state.finance.prize_money_races_paid,
        "prize_money_total_races": state.finance.prize_money_total_races,
        "transactions": transactions,
        "summary": summary,
        "track_profit_loss": report["track_profit_loss"],
        "overview": {
            "projected_end_balance": projected_end_balance,
            "next_race_income": next_race_income,
            "next_race_outgoings": next_race_outgoings,
            "next_race_net": next_race_net,
            "prize_outlook": prize_outlook,
            "contract_alerts": contract_alerts,
            "facilities_status": (
                f"${facilities_remaining:,} remaining over "
                f"{max(int(state.finance.facilities_upgrade_total_races or 0) - int(state.finance.facilities_upgrade_races_paid or 0), 0)} installments."
                if state.finance.facilities_upgrade_active and facilities_remaining > 0
                else "No active facilities financing."
            ),
        },
        "sponsor": {
            "name": sponsor_name,
            "annual_value": sponsor_yearly,
            "installment": sponsor_installment,
            "paid_so_far": sponsor_paid_so_far,
            "remaining": sponsor_remaining,
            "contract_length": int(player_team.title_sponsor_contract_length or 0) if player_team else 0,
            "pending_replacement": sponsor_pending_replacement,
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
            "contract_length": int(player_team.engine_supplier_contract_length or 0) if player_team else 0,
            "pending_replacement": engine_supplier_pending_replacement,
            "builds_own_engine": bool(getattr(player_team, "builds_own_engine", False)) if player_team else False,
        },
        "tyre_supplier": {
            "name": tyre_supplier_name,
            "deal": player_team.tyre_supplier_deal if player_team else None,
            "annual_value": tyre_supplier_yearly,
            "installment": tyre_supplier_installment,
            "paid_so_far": tyre_supplier_paid_so_far,
            "remaining": tyre_supplier_remaining,
            "contract_length": int(player_team.tyre_supplier_contract_length or 0) if player_team else 0,
            "pending_replacement": tyre_supplier_pending_replacement,
        },
        "fuel_supplier": {
            "name": fuel_supplier_name,
            "deal": player_team.fuel_supplier_deal if player_team else None,
            "annual_value": fuel_supplier_yearly,
            "installment": fuel_supplier_installment,
            "paid_so_far": fuel_supplier_paid_so_far,
            "remaining": fuel_supplier_remaining,
            "direction": "income" if fuel_supplier_yearly < 0 else "expense",
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
