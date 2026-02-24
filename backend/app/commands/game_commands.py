import json
import logging

from app.core.crash_damage import CrashDamageManager
from app.core.driver_wages import DriverWageManager
from app.core.engine_supplier_costs import EngineSupplierCostManager
from app.core.finance_reporting import build_finance_report
from app.core.grid import GridManager
from app.core.prize_money import PrizeMoneyManager
from app.core.retirement import RetirementManager
from app.core.roster import load_roster
from app.core.sponsorships import SponsorshipManager
from app.core.transport import TransportManager
from app.core.transfers import TransferManager
from app.core.tyre_supplier_costs import TyreSupplierCostManager
from app.core.workforce_costs import WorkforceCostManager
from app.models.calendar import Calendar
from app.models.email import EmailCategory
from app.models.finance import Finance, TransactionCategory
from app.models.state import GameState
from app.race.race_manager import RaceManager


def load_default_state() -> GameState:
    (
        teams,
        drivers,
        year,
        events,
        circuits,
        technical_directors,
        commercial_managers,
        title_sponsors,
        engine_suppliers,
        tyre_suppliers,
    ) = load_roster(
        year=0,
        include_technical_directors=True,
        include_commercial_managers=True,
        include_title_sponsors=True,
        include_engine_suppliers=True,
        include_tyre_suppliers=True,
    )
    calendar = Calendar(events=events, current_week=1)
    return GameState(
        year=year,
        teams=teams,
        drivers=drivers,
        technical_directors=technical_directors,
        commercial_managers=commercial_managers,
        title_sponsors=title_sponsors,
        engine_suppliers=engine_suppliers,
        tyre_suppliers=tyre_suppliers,
        calendar=calendar,
        circuits=circuits,
    )


def handle_load_roster(logger: logging.Logger):
    try:
        state = load_default_state()
        grid_json = GridManager().get_grid_json(state)
        grid_data = json.loads(grid_json)
        return state, {
            "status": "success",
            "message": f"Roster loaded for {state.year}",
            "data": grid_data,
        }
    except Exception as e:
        logger.error(f"Error loading roster: {e}")
        return None, {"status": "error", "message": str(e)}


def handle_start_career(state: GameState | None, logger: logging.Logger, team_name: str | None = None):
    try:
        current_state = state or load_default_state()
        selected_team_name = (team_name or "Warrick").strip()
        selected_team = next((t for t in current_state.teams if t.name == selected_team_name), None)
        if not selected_team:
            return current_state, {"status": "error", "message": f"Team '{selected_team_name}' not found in roster."}

        current_state.player_team_id = selected_team.id
        current_state.finance = Finance(balance=selected_team.balance)
        PrizeMoneyManager().assign_initial_entitlement_from_roster_order(current_state)

        current_state.add_email(
            sender="Board of Directors",
            subject="Welcome to Pitwall",
            body=(
                f"Welcome to {selected_team.name}! As the new Team Principal, you have full control over the team's "
                "strategy, development, and driver lineup. We're counting on you to lead us to glory. Good luck!"
            ),
            category=EmailCategory.GENERAL,
        )

        final_season_drivers = RetirementManager().mark_final_season_drivers(current_state)
        if final_season_drivers:
            lines = [f"- {d['name']} ({d['team_name']}), age {d['age']}" for d in final_season_drivers]
            current_state.add_email(
                sender="Competition Office",
                subject=f"Retirement Watch: {current_state.year} Final Seasons",
                body=("The following drivers have announced this will be their final season:\n\n" + "\n".join(lines)),
                category=EmailCategory.SEASON,
            )

        GridManager().capture_season_snapshot(current_state, year=current_state.year)
        TransferManager().recompute_ai_signings(current_state)
        return current_state, {
            "type": "game_started",
            "status": "success",
            "data": {
                "team_name": selected_team.name,
                "week_display": current_state.week_display,
                "next_event_display": current_state.next_event_display,
                "year": current_state.year,
                "balance": current_state.finance.balance,
                "unread_count": sum(1 for e in current_state.emails if not e.read),
            },
        }
    except Exception as e:
        logger.error(f"Error starting career: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_simulate_race(state: GameState, logger: logging.Logger):
    try:
        race_result = RaceManager().simulate_race(state)
        current_event = state.calendar.current_event
        event_name = race_result.get("event_name", "Grand Prix")

        PrizeMoneyManager().process_race_payout(state)
        sponsorship_charge = SponsorshipManager().apply_for_event(state, current_event)
        DriverWageManager().charge_for_event(state, current_event)
        workforce_charge = WorkforceCostManager().charge_for_event(state, current_event)
        engine_supplier_charge = EngineSupplierCostManager().charge_for_event(state, current_event)
        tyre_supplier_charge = TyreSupplierCostManager().charge_for_event(state, current_event)
        transport_charge = TransportManager().charge_for_event(state, current_event, attended=True)
        crash_damage_charges = CrashDamageManager().charge_for_race(state, race_result, current_event)

        if transport_charge:
            state.add_email(
                sender="Logistics Coordinator",
                subject=f"Transport Confirmed: {transport_charge.event_name}",
                body=(
                    f"Transport for {transport_charge.event_name} has been confirmed.\n\n"
                    f"Destination: {transport_charge.country}\n"
                    f"Cost: ${transport_charge.applied_cost:,}"
                ),
                category=EmailCategory.GENERAL,
            )
        if sponsorship_charge:
            state.add_email(
                sender="Commercial Department",
                subject=f"Sponsorship Payment Received: {sponsorship_charge.event_name}",
                body=(
                    f"Title sponsor installment received from {sponsorship_charge.sponsor_name}.\n\n"
                    f"Amount: ${sponsorship_charge.applied_income:,}\n"
                    f"Annual deal value: ${sponsorship_charge.yearly_value:,}"
                ),
                category=EmailCategory.GENERAL,
            )
        if workforce_charge:
            state.add_email(
                sender="HR & Operations",
                subject=f"Workforce Payroll Processed: {workforce_charge.event_name}",
                body=(
                    f"Race workforce payroll has been processed for {workforce_charge.event_name}.\n\n"
                    f"Staff count: {workforce_charge.workforce}\n"
                    f"Cost this race: ${workforce_charge.applied_cost:,}\n"
                    f"(Based on average annual wage ${workforce_charge.annual_avg_wage:,})"
                ),
                category=EmailCategory.GENERAL,
            )
        if engine_supplier_charge:
            state.add_email(
                sender="Procurement Department",
                subject=f"Engine Supplier Invoice: {engine_supplier_charge.event_name}",
                body=(
                    f"Engine supplier race fee has been processed for {engine_supplier_charge.event_name}.\n\n"
                    f"Supplier: {engine_supplier_charge.supplier_name}\n"
                    f"Deal: {engine_supplier_charge.deal_type}\n"
                    f"Cost this race: ${engine_supplier_charge.applied_cost:,}\n"
                    f"Annual contract value: ${engine_supplier_charge.yearly_cost:,}"
                ),
                category=EmailCategory.GENERAL,
            )
        if tyre_supplier_charge:
            state.add_email(
                sender="Procurement Department",
                subject=f"Tyre Supplier Invoice: {tyre_supplier_charge.event_name}",
                body=(
                    f"Tyre supplier race fee has been processed for {tyre_supplier_charge.event_name}.\n\n"
                    f"Supplier: {tyre_supplier_charge.supplier_name}\n"
                    f"Deal: {tyre_supplier_charge.deal_type}\n"
                    f"Cost this race: ${tyre_supplier_charge.applied_cost:,}\n"
                    f"Annual contract value: ${tyre_supplier_charge.yearly_cost:,}"
                ),
                category=EmailCategory.GENERAL,
            )
        if crash_damage_charges:
            total_damage = sum(c.applied_cost for c in crash_damage_charges)
            lines = "\n".join(f"- {c.driver_name}: {c.tier.title()} damage (${c.applied_cost:,})" for c in crash_damage_charges)
            state.add_email(
                sender="Chief Mechanic",
                subject=f"Crash Damage Report: {race_result.get('event_name', 'Grand Prix')}",
                body=f"The following crash repair work has been logged:\n\n{lines}\n\nTotal repair cost: ${total_damage:,}",
                category=EmailCategory.GENERAL,
            )

        race_transactions = [
            t for t in state.finance.transactions
            if t.week == state.calendar.current_week and t.year == state.year and t.event_name == event_name and t.event_type == "RACE"
        ]
        if race_transactions:
            income_total = sum(t.amount for t in race_transactions if t.amount > 0)
            expense_total = sum(-t.amount for t in race_transactions if t.amount < 0)
            net_total = income_total - expense_total

            def category_total(category):
                return sum(t.amount for t in race_transactions if t.category == category)

            prize_total = category_total(TransactionCategory.PRIZE_MONEY)
            sponsorship_total = category_total(TransactionCategory.SPONSORSHIP)
            driver_wage_total = category_total(TransactionCategory.DRIVER_WAGES)
            workforce_total = category_total(TransactionCategory.WORKFORCE_WAGES)
            engine_supplier_total = category_total(TransactionCategory.ENGINE_SUPPLIER)
            tyre_supplier_total = category_total(TransactionCategory.TYRE_SUPPLIER)
            transport_total = category_total(TransactionCategory.TRANSPORT)
            crash_total = category_total(TransactionCategory.CRASH_DAMAGE)
            state.add_email(
                sender="Finance Department",
                subject=f"Race Finance Summary: {event_name}",
                body=(
                    f"Financial summary for {event_name}:\n\n"
                    f"Prize money: {'+' if prize_total >= 0 else '-'}${abs(prize_total):,}\n"
                    f"Sponsorship: {'+' if sponsorship_total >= 0 else '-'}${abs(sponsorship_total):,}\n"
                    f"Driver wages: {'+' if driver_wage_total >= 0 else '-'}${abs(driver_wage_total):,}\n"
                    f"Workforce payroll: {'+' if workforce_total >= 0 else '-'}${abs(workforce_total):,}\n"
                    f"Engine supplier: {'+' if engine_supplier_total >= 0 else '-'}${abs(engine_supplier_total):,}\n"
                    f"Tyre supplier: {'+' if tyre_supplier_total >= 0 else '-'}${abs(tyre_supplier_total):,}\n"
                    f"Transport: {'+' if transport_total >= 0 else '-'}${abs(transport_total):,}\n"
                    f"Crash damage: {'+' if crash_total >= 0 else '-'}${abs(crash_total):,}\n\n"
                    f"Income: ${income_total:,}\nExpenses: ${expense_total:,}\nNet: {'+' if net_total >= 0 else '-'}${abs(net_total):,}"
                ),
                category=EmailCategory.GENERAL,
            )

        winner = race_result["results"][0]
        player_results = [r for r in race_result["results"] if r["team_id"] == state.player_team_id]
        player_lines = ""
        for pr in player_results:
            result_label = f"P{pr['position']}" if pr.get("position") else pr.get("status", "DNF")
            player_lines += f"\n  {result_label} - {pr['driver_name']} ({pr['points']} pts)"
        state.add_email(
            sender="Race Director",
            subject=f"Race Report: {event_name}",
            body=f"The {event_name} has concluded.\n\nWinner: {winner['driver_name']} ({winner['team_name']})\n\nYour Team Results:{player_lines}",
            category=EmailCategory.RACE_RESULT,
        )
        return state, {"type": "race_result", "status": "success", "data": race_result}
    except Exception as e:
        logger.error(f"Error simulating race: {e}")
        return state, {"status": "error", "message": str(e)}


def build_finance_payload(state: GameState):
    transactions = [t.model_dump() for t in state.finance.transactions]
    report = build_finance_report(state)
    player_team = state.player_team
    sponsor_name = player_team.title_sponsor_name if player_team else None
    sponsor_yearly = player_team.title_sponsor_yearly if player_team else 0
    sponsor_installment = SponsorshipManager().calculate_race_installment(
        sponsor_yearly, state.finance.prize_money_total_races or 0
    ) if sponsor_name else 0
    sponsor_paid_so_far = sum(
        t.amount for t in state.finance.transactions
        if t.category == TransactionCategory.SPONSORSHIP and t.year == state.year and t.amount > 0
    )
    sponsor_remaining = max(sponsor_yearly - sponsor_paid_so_far, 0) if sponsor_name else 0
    race_count = state.finance.prize_money_total_races or max(
        1, sum(1 for e in state.calendar.events if getattr(e.type, "value", e.type) == "RACE")
    )

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
    }
