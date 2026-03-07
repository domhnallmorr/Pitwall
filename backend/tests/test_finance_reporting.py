from app.core.finance_reporting import build_finance_report
from app.models.state import GameState
from app.models.calendar import Calendar
from app.models.finance import Finance, TransactionCategory


def test_build_finance_report_summarizes_and_groups_by_track():
    state = GameState(year=1998, teams=[], drivers=[], calendar=Calendar(events=[]), circuits=[])
    finance = Finance(balance=0)

    finance.add_transaction(
        week=10,
        year=1998,
        amount=2_000_000,
        category=TransactionCategory.PRIZE_MONEY,
        description="Prize",
        event_name="Albert Park",
        event_type="RACE",
        circuit_country="Australia",
    )
    finance.add_transaction(
        week=10,
        year=1998,
        amount=500_000,
        category=TransactionCategory.SPONSORSHIP,
        description="Sponsor",
        event_name="Albert Park",
        event_type="RACE",
        circuit_country="Australia",
    )
    finance.add_transaction(
        week=10,
        year=1998,
        amount=-350_000,
        category=TransactionCategory.TRANSPORT,
        description="Transport",
        event_name="Albert Park",
        event_type="RACE",
        circuit_country="Australia",
    )
    finance.add_transaction(
        week=11,
        year=1998,
        amount=-80_000,
        category=TransactionCategory.DRIVER_WAGES,
        description="Wage",
    )
    finance.add_transaction(
        week=10,
        year=1998,
        amount=-120_000,
        category=TransactionCategory.WORKFORCE_WAGES,
        description="Workforce payroll",
        event_name="Albert Park",
        event_type="RACE",
        circuit_country="Australia",
    )
    state.finance = finance

    report = build_finance_report(state)

    assert report["summary"]["income_total"] == 2_500_000
    assert report["summary"]["expense_total"] == 550_000
    assert report["summary"]["net_profit_loss"] == 1_950_000
    assert report["summary"]["transport_total"] == 350_000
    assert report["summary"]["workforce_total"] == 120_000
    assert report["summary"]["engine_supplier_total"] == 0
    assert report["summary"]["tyre_supplier_total"] == 0
    assert report["summary"]["fuel_supplier_total"] == 0
    assert report["summary"]["sponsorship_total"] == 500_000

    assert len(report["track_profit_loss"]) == 1
    track = report["track_profit_loss"][0]
    assert track["track"] == "Albert Park"
    assert track["country"] == "Australia"
    assert track["income"] == 2_500_000
    assert track["expense"] == 470_000
    assert track["net"] == 2_030_000
