import logging

from app.core.crash_damage import CrashDamageManager
from app.core.driver_wages import DriverWageManager
from app.core.engine_supplier_costs import EngineSupplierCostManager
from app.core.facilities_upgrades import FacilitiesUpgradeManager
from app.core.fuel_supplier_costs import FuelSupplierCostManager
from app.core.prize_money import PrizeMoneyManager
from app.core.sponsorships import SponsorshipManager
from app.core.transport import TransportManager
from app.core.tyre_supplier_costs import TyreSupplierCostManager
from app.core.workforce_costs import WorkforceCostManager
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.calendar import EventType
from app.race.race_manager import RaceManager


def _build_race_weekend_payload(state: GameState) -> dict:
    current_event = state.calendar.current_event
    if current_event is None or current_event.type != EventType.RACE:
        return {}

    circuit = RaceManager()._get_circuit(state)
    event_key = f"{state.year}_{current_event.week}_{current_event.name}"
    qualifying_results = list(state.qualifying_results_by_event.get(event_key, []))
    event_processed = f"{current_event.week}_{current_event.name}" in state.events_processed

    return {
        "event_name": current_event.name,
        "week": current_event.week,
        "circuit_name": circuit.name,
        "circuit_location": circuit.location,
        "circuit_country": circuit.country,
        "laps": circuit.laps,
        "qualifying_complete": bool(qualifying_results),
        "race_complete": event_processed,
        "qualifying_results": qualifying_results,
    }


def handle_get_race_weekend(state: GameState, logger: logging.Logger):
    try:
        payload = _build_race_weekend_payload(state)
        if not payload:
            return state, {"status": "error", "message": "No active race weekend"}
        return state, {"type": "race_weekend", "status": "success", "data": payload}
    except Exception as e:
        logger.error(f"Error building race weekend payload: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_simulate_qualifying(state: GameState, logger: logging.Logger):
    try:
        result = RaceManager().simulate_qualifying(state)
        return state, {"type": "qualifying_result", "status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error simulating qualifying: {e}")
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
        fuel_supplier_charge = FuelSupplierCostManager().charge_for_event(state, current_event)
        transport_charge = TransportManager().charge_for_event(state, current_event, attended=True)
        crash_damage_charges = CrashDamageManager().charge_for_race(state, race_result, current_event)
        facilities_upgrade_charge = FacilitiesUpgradeManager().charge_for_event(state, current_event)

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
                    f"Commercial income received for {sponsorship_charge.event_name}.\n\n"
                    f"Title sponsor ({sponsorship_charge.title_sponsor_name}): ${sponsorship_charge.title_income:,}\n"
                    f"Other sponsorship: ${sponsorship_charge.other_income:,}\n"
                    f"Total this race: ${sponsorship_charge.applied_income:,}\n\n"
                    f"Title annual value: ${sponsorship_charge.title_yearly_value:,}\n"
                    f"Other annual value: ${sponsorship_charge.other_yearly_value:,}"
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
        if fuel_supplier_charge:
            is_income = fuel_supplier_charge.applied_amount > 0
            state.add_email(
                sender="Procurement Department",
                subject=f"Fuel Supplier Settlement: {fuel_supplier_charge.event_name}",
                body=(
                    f"Fuel supplier settlement has been processed for {fuel_supplier_charge.event_name}.\n\n"
                    f"Supplier: {fuel_supplier_charge.supplier_name}\n"
                    f"Deal: {fuel_supplier_charge.deal_type}\n"
                    f"This race: {'+' if is_income else '-'}${abs(fuel_supplier_charge.applied_amount):,}\n"
                    f"Annual contract value: {'+' if fuel_supplier_charge.yearly_cost < 0 else '-'}${abs(fuel_supplier_charge.yearly_cost):,}"
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
        if facilities_upgrade_charge:
            state.add_email(
                sender="Infrastructure Department",
                subject=f"Facilities Upgrade Installment: {facilities_upgrade_charge.event_name}",
                body=(
                    f"A facilities upgrade installment has been processed.\n\n"
                    f"Cost this race: ${facilities_upgrade_charge.applied_cost:,}\n"
                    f"Remaining balance: ${facilities_upgrade_charge.remaining_cost:,}\n"
                    f"Installments paid: {facilities_upgrade_charge.races_paid}/{facilities_upgrade_charge.total_races}"
                ),
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
            fuel_supplier_total = category_total(TransactionCategory.FUEL_SUPPLIER)
            transport_total = category_total(TransactionCategory.TRANSPORT)
            crash_total = category_total(TransactionCategory.CRASH_DAMAGE)
            facilities_total = category_total(TransactionCategory.FACILITIES)
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
                    f"Fuel supplier: {'+' if fuel_supplier_total >= 0 else '-'}${abs(fuel_supplier_total):,}\n"
                    f"Transport: {'+' if transport_total >= 0 else '-'}${abs(transport_total):,}\n"
                    f"Crash damage: {'+' if crash_total >= 0 else '-'}${abs(crash_total):,}\n\n"
                    f"Facilities financing: {'+' if facilities_total >= 0 else '-'}${abs(facilities_total):,}\n\n"
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
