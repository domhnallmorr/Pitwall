import pytest
from unittest.mock import MagicMock
from pw_model.finance.finance_model import FinanceModel

# Create a dummy model fixture with the minimal attributes needed.
@pytest.fixture
def dummy_model():
    model = MagicMock()
    # game_data: get_number_of_races is used in driver_race_costs and supplier payments.
    model.game_data.get_number_of_races.return_value = 10

    # Set up a dummy season calendar (used when updating balance history)
    dummy_calendar = MagicMock()
    dummy_calendar.current_week = 1
    # For transport costs: current_track_model is used to get the country.
    dummy_track = MagicMock()
    dummy_track.country = "Australia"
    dummy_calendar.current_track_model = dummy_track
    dummy_calendar.countries = ["Australia"]
    model.season = MagicMock()
    model.season.calendar = dummy_calendar

    # Provide a dummy inbox to capture email calls.
    model.inbox = MagicMock()
    return model

# Create a dummy team_model fixture with the minimal attributes and sub-objects.
@pytest.fixture
def dummy_team_model(dummy_model):
    team = MagicMock()
    team.number_of_staff = 10

    # Create dummy technical director with a contract salary.
    td = MagicMock()
    td.contract.salary = 2_600_000  # yearly salary
    team.technical_director_model = td

    # Create dummy commercial manager with a contract salary.
    cm = MagicMock()
    cm.contract.salary = 2_800_000  # yearly salary
    team.commercial_manager_model = cm

    # Create dummy driver models with contracts. (For driver race costs)
    d1 = MagicMock()
    d1.contract.salary = 4_000_000
    team.driver1_model = d1

    d2 = MagicMock()
    d2.contract.salary = 4_000_000
    team.driver2_model = d2

    # Create a dummy supplier model.
    supplier = MagicMock()
    supplier.engine_supplier_cost = 2_000_000  # so per race: 2,000,000/10 = 200,000
    supplier.tyre_supplier_cost = 1_800_000    # so per race: 1,800,000/10 = 180,000
    supplier.engine_payments = []
    supplier.tyre_payments = []

    # We simulate process_race_payments as in the actual implementation.
    def fake_process_race_payments():
        engine_payment = int(supplier.engine_supplier_cost / dummy_model.game_data.get_number_of_races())
        tyre_payment = int(supplier.tyre_supplier_cost / dummy_model.game_data.get_number_of_races())
        supplier.engine_payments.append(engine_payment)
        supplier.tyre_payments.append(tyre_payment)
    supplier.process_race_payments.side_effect = fake_process_race_payments

    team.supplier_model = supplier

    return team

def test_weekly_update(dummy_model, dummy_team_model):
    """
    Test that weekly_update adjusts the balance correctly:
      - Adds weekly prize money,
      - Deducts staff cost (based on number_of_staff),
      - Deducts weekly manager costs,
      - Deducts car development cost.
    Also verifies that the balance history is updated and that there is no debt.
    """
    # Use finishing_position 0 -> prize money = 33,000,000
    fm = FinanceModel(
        dummy_model,
        dummy_team_model,
        opening_balance=100_000_000,
        other_sponsorship=0,
        title_sponsor="TestSponsor",
        finishing_position=0,
    )

    # Override the car development weekly payment to a fixed value.
    fm.car_development_costs_model.process_weekly_payment = MagicMock(return_value=100_000)

    initial_balance = fm.balance

    fm.weekly_update()

    # Calculations:
    # Prize money addition: int(33,000,000 / 52)
    prize_weekly = int(33_000_000 / 52)  # ~634615
    # Staff cost: (28,000 yearly / 52) * number_of_staff (10)
    staff_weekly = int((28_000 / 52) * dummy_team_model.number_of_staff)  # ~5384
    # Technical director weekly: int(2,600,000 / 52) = 50,000
    td_weekly = int(2_600_000 / 52)
    # Commercial manager weekly: int(2,800,000 / 52) ≈ 53,846
    cm_weekly = int(2_800_000 / 52)
    # Car development weekly cost (overridden) = 100,000
    car_dev_weekly = 100_000

    expected_change = prize_weekly - staff_weekly - td_weekly - cm_weekly - car_dev_weekly
    expected_balance = initial_balance + expected_change

    assert fm.balance == expected_balance
    # Verify that balance history is updated with the new balance.
    assert fm.balance_history[-1] == expected_balance
    # And since the balance is positive, consecutive_weeks_in_debt should be 0.
    assert fm.consecutive_weeks_in_debt == 0

def test_post_race_actions(dummy_model, dummy_team_model):
    """
    Test that post_race_actions:
      - Subtracts driver race costs, transport, damage, and supplier payments,
      - Adds sponsor income,
      - Calls the new_race_finance_email with the correct parameters.
    """
    fm = FinanceModel(
        dummy_model,
        dummy_team_model,
        opening_balance=100_000_000,
        other_sponsorship=0,
        title_sponsor="TestSponsor",
        finishing_position=0,
    )

    initial_balance = fm.balance

    # --- Set up fakes for external cost calculations ---

    # For transport costs: override gen_race_transport_cost to simulate a cost of 300,000.
    fm.transport_costs_model.costs_by_race = []
    def fake_gen_race_transport_cost():
        fm.transport_costs_model.costs_by_race.append(300_000)
    fm.transport_costs_model.gen_race_transport_cost = fake_gen_race_transport_cost

    # For damage costs: override calculate_race_damage_costs to simulate a damage cost of 150,000.
    def fake_damage_costs(player1_crashed, player2_crashed):
        fm.damage_costs_model.damage_costs.append(150_000)
    fm.damage_costs_model.calculate_race_damage_costs = fake_damage_costs

    # For sponsors: override process_sponsor_post_race_payments to simulate:
    #   - Other sponsor payment: 50,000
    #   - Title sponsor payment: 100,000
    fm.sponsorship_model.other_sponser_payments = []
    fm.sponsorship_model.title_sponser_payments = []
    def fake_sponsor_payments():
        fm.sponsorship_model.other_sponser_payments.append(50_000)
        fm.sponsorship_model.title_sponser_payments.append(100_000)
    fm.sponsorship_model.process_sponsor_post_race_payments = fake_sponsor_payments

    # Now call post_race_actions.
    # Let’s simulate that driver1 crashed and driver2 did not.
    fm.post_race_actions(player_driver1_crashed=True, player_driver2_crashed=False)

    # --- Calculate expected changes ---
    # Driver race costs: each driver salary 4,000,000 over 10 races → 400,000 per driver; sum = 800,000.
    driver_race_costs = 800_000

    # Transport cost is set to 300,000.
    transport_cost = 300_000

    # Damage cost is set to 150,000.
    damage_cost = 150_000

    # Supplier payments: process_race_payments (using our dummy_team_model.supplier_model)
    #   engine_payment = 2,000,000 / 10 = 200,000 and tyre_payment = 1,800,000 / 10 = 180,000.
    engine_payment = 200_000
    tyre_payment = 180_000

    # In apply_race_costs, the following amounts are deducted:
    # driver_race_costs + transport_cost + damage_cost + engine_payment + tyre_payment =
    # 800,000 + 300,000 + 150,000 + 200,000 + 180,000 = 1,630,000 deducted.
    # Then process_race_income adds sponsor payments: 50,000 + 100,000 = 150,000.
    # So net change = -1,630,000 + 150,000 = -1,480,000.
    net_change = -1_630_000 + 150_000
    expected_balance = initial_balance + net_change

    # Verify final balance.
    assert fm.balance == expected_balance

    # Profit passed to email is the change in balance.
    expected_profit = net_change

    # Verify that new_race_finance_email was called with the expected parameters:
    # (transport_cost, damage_cost, title_sponsor_payment, engine_payment, tyre_payment, profit, driver_race_costs)
    dummy_model.inbox.new_race_finance_email.assert_called_with(
        transport_cost,
        damage_cost,
        100_000,      # title sponsor payment as simulated
        engine_payment,
        tyre_payment,
        expected_profit,
        driver_race_costs,
    )
