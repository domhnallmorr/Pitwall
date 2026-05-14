from unittest.mock import Mock, patch

from app.commands.staff_commands import (
    handle_build_spare_set,
    handle_offer_driver,
    handle_get_engine_supplier_replacement_candidates,
    handle_get_tyre_negotiation_market,
    handle_get_technical_director_replacement_candidates,
    handle_get_manager_replacement_candidates,
    handle_get_tyre_supplier_replacement_candidates,
    handle_get_title_sponsor_replacement_candidates,
    handle_get_replacement_candidates,
    handle_replace_commercial_manager,
    handle_replace_engine_supplier,
    handle_replace_technical_director,
    handle_replace_tyre_supplier,
    handle_sign_tyre_negotiated_deal,
    handle_replace_title_sponsor,
    handle_replace_driver,
    handle_repair_chassis_wear,
    handle_set_race_chassis_assignments,
    handle_set_test_chassis,
    handle_start_car_development,
    handle_start_tyre_negotiation,
    handle_update_tyre_negotiation_staff,
)
from app.models.chassis import Chassis
from app.models.calendar import Calendar, Event, EventType
from app.models.commercial_manager import CommercialManager
from app.models.driver import Driver
from app.models.state import GameState, PlayerConstructionProject
from app.models.team import Team
from app.models.technical_director import TechnicalDirector
from app.models.title_sponsor import TitleSponsor
from app.models.engine_supplier import EngineSupplier
from app.models.tyre_supplier import TyreSupplier


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2, workforce=120, engineering_staff=54, mechanics_staff=58, car_wear=10, title_sponsor_name="Windale", title_sponsor_yearly=32_500_000, title_sponsor_contract_length=1, engine_supplier_name="Mechatron", engine_supplier_deal="customer", engine_supplier_contract_length=1, tyre_supplier_name="Greatday", tyre_supplier_deal="partner", tyre_supplier_contract_length=1)],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, contract_length=1, speed=80),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, contract_length=2, speed=70),
            Driver(id=3, name="Free Driver", age=22, country="France", team_id=None, contract_length=0, speed=65),
        ],
        commercial_managers=[
            CommercialManager(id=11, name="Jace Whitman", country="United Kingdom", age=29, skill=70, contract_length=1, salary=300_000, team_id=1),
            CommercialManager(id=12, name="Free CM", country="France", age=40, skill=55, contract_length=0, salary=0, team_id=None),
        ],
        technical_directors=[
            TechnicalDirector(id=21, name="Peter Heed", country="United Kingdom", age=52, skill=75, contract_length=1, salary=4_800_000, team_id=1),
            TechnicalDirector(id=22, name="Free TD", country="France", age=44, skill=68, contract_length=0, salary=0, team_id=None),
        ],
        title_sponsors=[
            TitleSponsor(id=31, name="Windale", wealth=70, start_year=0),
            TitleSponsor(id=32, name="Bright Shot", wealth=85, start_year=0),
        ],
        engine_suppliers=[
            EngineSupplier(id=40, name="Ferano", country="Italy", resources=90, power=72, start_year=0),
            EngineSupplier(id=41, name="Mechatron", country="France", resources=55, power=60, start_year=0),
            EngineSupplier(id=42, name="Frost", country="USA", resources=65, power=38, start_year=0),
        ],
        tyre_suppliers=[
            TyreSupplier(id=41, name="Greatday", country="USA", wear=60, grip=80, start_year=0),
            TyreSupplier(id=42, name="Spanrock", country="Japan", wear=80, grip=70, start_year=0),
        ],
        calendar=Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=10),
        circuits=[],
        player_team_id=1,
        player_chassis=[
            Chassis(id=1, team_id=1, name="Chassis 1", wear=10),
            Chassis(id=2, team_id=1, name="Chassis 2", wear=4),
            Chassis(id=3, team_id=1, name="Chassis 3", wear=0),
        ],
        player_spares=3,
        player_test_chassis_id=1,
        player_race_chassis_assignments={1: 1, 2: 2},
    )


def test_replace_driver_requires_driver_id():
    state = create_state()
    logger = Mock()
    _, result = handle_replace_driver(state, logger, driver_id=None)
    assert result["status"] == "error"


def test_replace_driver_handles_value_error():
    state = create_state()
    logger = Mock()
    with patch("app.commands.staff_commands.TransferManager.sign_player_replacement", side_effect=ValueError("bad signing")):
        _, result = handle_replace_driver(state, logger, driver_id=1)
    assert result["status"] == "error"
    assert result["message"] == "bad signing"


def test_replace_driver_handles_unexpected_error_and_logs():
    state = create_state()
    logger = Mock()
    with patch("app.commands.staff_commands.TransferManager.sign_player_replacement", side_effect=RuntimeError("boom")):
        _, result = handle_replace_driver(state, logger, driver_id=1)
    assert result["status"] == "error"
    assert result["message"] == "boom"
    logger.error.assert_called_once()


def test_get_replacement_candidates_validates_driver():
    state = create_state()
    logger = Mock()
    assert handle_get_replacement_candidates(state, logger, driver_id=None)["status"] == "error"
    assert handle_get_replacement_candidates(state, logger, driver_id=999)["status"] == "error"


def test_get_replacement_candidates_handles_transfer_errors():
    state = create_state()
    logger = Mock()
    with patch("app.commands.staff_commands.TransferManager.get_player_replacement_candidates", side_effect=ValueError("blocked")):
        result = handle_get_replacement_candidates(state, logger, driver_id=1)
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_commands.TransferManager.get_player_replacement_candidates", side_effect=RuntimeError("nope")):
        result = handle_get_replacement_candidates(state, logger, driver_id=1)
    assert result["status"] == "error"
    assert result["message"] == "nope"
    assert logger.error.called


def test_offer_driver_validates_and_handles_errors():
    state = create_state()
    logger = Mock()

    _, result = handle_offer_driver(state, logger, driver_id=None, incoming_driver_id=3, salary_offer=500000, contract_length=2)
    assert result["status"] == "error"

    with patch("app.commands.staff_market_commands.PlayerDriverNegotiationManager.submit_offer", side_effect=ValueError("blocked")):
        _, result = handle_offer_driver(state, logger, driver_id=1, incoming_driver_id=3, salary_offer=500000, contract_length=2)
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_market_commands.PlayerDriverNegotiationManager.submit_offer", side_effect=RuntimeError("boom")):
        _, result = handle_offer_driver(state, logger, driver_id=1, incoming_driver_id=3, salary_offer=500000, contract_length=2)
    assert result["status"] == "error"
    assert result["message"] == "boom"
    assert logger.error.called


def test_replace_commercial_manager_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    _, result = handle_replace_commercial_manager(state, logger, manager_id=None)
    assert result["status"] == "error"

    with patch("app.commands.staff_commands.CommercialManagerTransferManager.sign_player_replacement", side_effect=ValueError("bad")):
        _, result = handle_replace_commercial_manager(state, logger, manager_id=11)
    assert result["status"] == "error"
    assert result["message"] == "bad"

    with patch("app.commands.staff_commands.CommercialManagerTransferManager.sign_player_replacement", side_effect=RuntimeError("oops")):
        _, result = handle_replace_commercial_manager(state, logger, manager_id=11)
    assert result["status"] == "error"
    assert result["message"] == "oops"


def test_get_manager_replacement_candidates_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_get_manager_replacement_candidates(state, logger, manager_id=None)["status"] == "error"
    assert handle_get_manager_replacement_candidates(state, logger, manager_id=999)["status"] == "error"

    with patch("app.commands.staff_commands.CommercialManagerTransferManager.get_player_replacement_candidates", side_effect=ValueError("blocked")):
        result = handle_get_manager_replacement_candidates(state, logger, manager_id=11)
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_commands.CommercialManagerTransferManager.get_player_replacement_candidates", side_effect=RuntimeError("fail")):
        result = handle_get_manager_replacement_candidates(state, logger, manager_id=11)
    assert result["status"] == "error"
    assert result["message"] == "fail"
    assert logger.error.called


def test_replace_technical_director_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    _, result = handle_replace_technical_director(state, logger, director_id=None)
    assert result["status"] == "error"

    with patch("app.commands.staff_commands.TechnicalDirectorTransferManager.sign_player_replacement", side_effect=ValueError("bad")):
        _, result = handle_replace_technical_director(state, logger, director_id=21)
    assert result["status"] == "error"
    assert result["message"] == "bad"

    with patch("app.commands.staff_commands.TechnicalDirectorTransferManager.sign_player_replacement", side_effect=RuntimeError("oops")):
        _, result = handle_replace_technical_director(state, logger, director_id=21)
    assert result["status"] == "error"
    assert result["message"] == "oops"


def test_get_technical_director_replacement_candidates_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_get_technical_director_replacement_candidates(state, logger, director_id=None)["status"] == "error"
    assert handle_get_technical_director_replacement_candidates(state, logger, director_id=999)["status"] == "error"

    with patch("app.commands.staff_commands.TechnicalDirectorTransferManager.get_player_replacement_candidates", side_effect=ValueError("blocked")):
        result = handle_get_technical_director_replacement_candidates(state, logger, director_id=21)
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_commands.TechnicalDirectorTransferManager.get_player_replacement_candidates", side_effect=RuntimeError("fail")):
        result = handle_get_technical_director_replacement_candidates(state, logger, director_id=21)
    assert result["status"] == "error"
    assert result["message"] == "fail"
    assert logger.error.called


def test_replace_title_sponsor_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    _, result = handle_replace_title_sponsor(state, logger, sponsor_name=None)
    assert result["status"] == "error"

    with patch("app.commands.staff_commands.TitleSponsorTransferManager.sign_player_replacement", side_effect=ValueError("bad")):
        _, result = handle_replace_title_sponsor(state, logger, sponsor_name="Windale")
    assert result["status"] == "error"
    assert result["message"] == "bad"

    with patch("app.commands.staff_commands.TitleSponsorTransferManager.sign_player_replacement", side_effect=RuntimeError("oops")):
        _, result = handle_replace_title_sponsor(state, logger, sponsor_name="Windale")
    assert result["status"] == "error"
    assert result["message"] == "oops"


def test_replace_engine_supplier_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    _, result = handle_replace_engine_supplier(state, logger, supplier_name=None)
    assert result["status"] == "error"

    with patch("app.commands.staff_commands.EngineSupplierTransferManager.sign_player_replacement", side_effect=ValueError("bad")):
        _, result = handle_replace_engine_supplier(state, logger, supplier_name="Mechatron")
    assert result["status"] == "error"
    assert result["message"] == "bad"

    with patch("app.commands.staff_commands.EngineSupplierTransferManager.sign_player_replacement", side_effect=RuntimeError("oops")):
        _, result = handle_replace_engine_supplier(state, logger, supplier_name="Mechatron")
    assert result["status"] == "error"
    assert result["message"] == "oops"


def test_get_title_sponsor_replacement_candidates_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_get_title_sponsor_replacement_candidates(state, logger, sponsor_name=None)["status"] == "error"
    assert handle_get_title_sponsor_replacement_candidates(state, logger, sponsor_name="Nope")["status"] == "error"

    with patch("app.commands.staff_commands.TitleSponsorTransferManager.get_player_replacement_candidates", side_effect=ValueError("blocked")):
        result = handle_get_title_sponsor_replacement_candidates(state, logger, sponsor_name="Windale")
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_commands.TitleSponsorTransferManager.get_player_replacement_candidates", side_effect=RuntimeError("fail")):
        result = handle_get_title_sponsor_replacement_candidates(state, logger, sponsor_name="Windale")
    assert result["status"] == "error"
    assert result["message"] == "fail"
    assert logger.error.called


def test_get_engine_supplier_replacement_candidates_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_get_engine_supplier_replacement_candidates(state, logger, supplier_name=None)["status"] == "error"
    assert handle_get_engine_supplier_replacement_candidates(state, logger, supplier_name="Nope")["status"] == "error"

    with patch("app.commands.staff_commands.EngineSupplierTransferManager.get_player_replacement_candidates", side_effect=ValueError("blocked")):
        result = handle_get_engine_supplier_replacement_candidates(state, logger, supplier_name="Mechatron")
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_commands.EngineSupplierTransferManager.get_player_replacement_candidates", side_effect=RuntimeError("fail")):
        result = handle_get_engine_supplier_replacement_candidates(state, logger, supplier_name="Mechatron")
    assert result["status"] == "error"
    assert result["message"] == "fail"
    assert logger.error.called


def test_replace_tyre_supplier_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    _, result = handle_replace_tyre_supplier(state, logger, supplier_name=None)
    assert result["status"] == "error"

    with patch("app.commands.staff_commands.TyreSupplierTransferManager.sign_player_replacement", side_effect=ValueError("bad")):
        _, result = handle_replace_tyre_supplier(state, logger, supplier_name="Greatday")
    assert result["status"] == "error"
    assert result["message"] == "bad"

    with patch("app.commands.staff_commands.TyreSupplierTransferManager.sign_player_replacement", side_effect=RuntimeError("oops")):
        _, result = handle_replace_tyre_supplier(state, logger, supplier_name="Greatday")
    assert result["status"] == "error"
    assert result["message"] == "oops"


def test_get_tyre_supplier_replacement_candidates_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_get_tyre_supplier_replacement_candidates(state, logger, supplier_name=None)["status"] == "error"
    assert handle_get_tyre_supplier_replacement_candidates(state, logger, supplier_name="Nope")["status"] == "error"

    with patch("app.commands.staff_commands.TyreSupplierTransferManager.get_player_replacement_candidates", side_effect=ValueError("blocked")):
        result = handle_get_tyre_supplier_replacement_candidates(state, logger, supplier_name="Greatday")
    assert result["status"] == "error"
    assert result["message"] == "blocked"

    with patch("app.commands.staff_commands.TyreSupplierTransferManager.get_player_replacement_candidates", side_effect=RuntimeError("fail")):
        result = handle_get_tyre_supplier_replacement_candidates(state, logger, supplier_name="Greatday")
    assert result["status"] == "error"
    assert result["message"] == "fail"
    assert logger.error.called


def test_tyre_negotiation_handlers_validate_and_handle_errors():
    state = create_state()
    logger = Mock()

    assert handle_get_tyre_negotiation_market(state, logger)["status"] == "success"
    _, result = handle_start_tyre_negotiation(state, logger, supplier_id=None)
    assert result["status"] == "error"
    _, result = handle_update_tyre_negotiation_staff(state, logger, assigned_staff=None)
    assert result["status"] == "error"
    _, result = handle_sign_tyre_negotiated_deal(state, logger, tier=None)
    assert result["status"] == "error"

    with patch("app.commands.staff_market_commands.PlayerTyreNegotiationManager.get_market_payload", side_effect=RuntimeError("boom")):
        result = handle_get_tyre_negotiation_market(state, logger)
    assert result["status"] == "error"


def test_start_car_development_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_start_car_development(state, logger, development_type=None)["status"] == "success"

    state = create_state()
    with patch("app.commands.staff_team_commands.PlayerCarDevelopmentManager.start", side_effect=ValueError("invalid")):
        result = handle_start_car_development(state, logger, development_type="current_year")
    assert result["status"] == "error"
    assert result["message"] == "invalid"

    with patch("app.commands.staff_team_commands.PlayerCarDevelopmentManager.start", side_effect=RuntimeError("x")):
        result = handle_start_car_development(state, logger, development_type="current_year")
    assert result["status"] == "error"
    assert result["message"] == "x"


def test_chassis_commands_validate_edge_cases_and_exceptions():
    state = create_state()
    logger = Mock()
    state.player_team_id = None
    assert handle_set_test_chassis(state, logger, chassis_id=1)["status"] == "error"

    state = create_state()
    state.player_chassis[2].wear = 0
    assert handle_repair_chassis_wear(state, logger, chassis_id=3, wear_points=10)["status"] == "error"
    assert handle_repair_chassis_wear(state, logger, chassis_id=1, wear_points=None)["status"] == "error"
    assert handle_repair_chassis_wear(state, logger, chassis_id=1, wear_points=0)["status"] == "error"
    state.player_spares = 0
    assert handle_repair_chassis_wear(state, logger, chassis_id=1, wear_points=1)["status"] == "error"
    assert handle_set_race_chassis_assignments(state, logger, driver1_chassis_id=1, driver2_chassis_id=1)["status"] == "error"

    state.player_chassis[0].wear = "bad"
    result = handle_repair_chassis_wear(state, logger, chassis_id=1, wear_points=1)
    assert result["status"] == "error"


def test_chassis_commands_apply_player_updates():
    state = create_state()
    logger = Mock()

    test_result = handle_set_test_chassis(state, logger, chassis_id=3)
    assert test_result["status"] == "success"
    assert state.player_test_chassis_id == 3

    race_result = handle_set_race_chassis_assignments(state, logger, driver1_chassis_id=2, driver2_chassis_id=3)
    assert race_result["status"] == "success"
    assert state.player_race_chassis_assignments == {1: 2, 2: 3}

    with patch("app.commands.staff_team_commands.random.randint", return_value=26):
        repair_result = handle_repair_chassis_wear(state, logger, chassis_id=2, wear_points=3)
    assert repair_result["status"] == "success"
    assert state.player_chassis[1].wear == 1
    assert repair_result["data"]["spares_used"] == 1
    assert state.player_spares == 2
    assert repair_result["data"]["mechanics_usage_percent_used"] == 22
    assert state.player_mechanics_usage_percent == 22


def test_chassis_repair_blocks_when_mechanics_capacity_is_exhausted():
    state = create_state()
    state.player_mechanics_usage_percent = 95
    state.player_mechanics_usage_week = 10
    state.player_mechanics_usage_year = 1998
    logger = Mock()

    result = handle_repair_chassis_wear(state, logger, chassis_id=1, wear_points=10)

    assert result["status"] == "error"
    assert "mechanics capacity" in result["message"]


def test_build_spare_set_updates_stock_and_records_cost():
    state = create_state()
    state.finance.balance = 500_000
    state.player_spares = 0
    logger = Mock()

    result = handle_build_spare_set(state, logger)

    assert result["status"] == "success"
    assert result["data"]["spares_before"] == 0
    assert result["data"]["spares_after"] == 1
    assert result["data"]["construction_usage_percent_before"] == 0
    assert result["data"]["construction_usage_percent_after"] == 45
    assert state.player_spares == 1
    assert state.player_construction_usage_percent == 45
    txs = [t for t in state.finance.transactions if t.category.value == "construction"]
    assert len(txs) == 1
    assert txs[0].amount == -52_500


def test_build_spare_set_blocks_when_stock_full_or_cash_missing():
    state = create_state()
    state.player_spares = 0
    logger = Mock()

    result = handle_build_spare_set(state, logger)
    assert result["status"] == "error"
    assert "Insufficient funds" in result["message"]

    state.finance.balance = 500_000
    state.player_spares = 10
    result = handle_build_spare_set(state, logger)
    assert result["status"] == "error"
    assert "full" in result["message"]


def test_build_spare_set_blocks_when_weekly_construction_capacity_is_used():
    state = create_state()
    state.finance.balance = 500_000
    state.player_construction_usage_percent = 90
    state.player_construction_usage_week = 10
    state.player_construction_usage_year = 1998
    logger = Mock()

    result = handle_build_spare_set(state, logger)

    assert result["status"] == "error"
    assert "capacity" in result["message"]


def test_build_spare_set_blocks_when_chassis_construction_uses_engineering_capacity():
    state = create_state()
    state.finance.balance = 500_000
    state.player_spares = 0
    state.player_construction_projects = [
        PlayerConstructionProject(
            active=True,
            scope="next_year",
            name="1999 Chassis",
            allocation_percent=70,
            assigned_engineers=38,
        )
    ]
    logger = Mock()

    result = handle_build_spare_set(state, logger)

    assert result["status"] == "error"
    assert "free engineering" in result["message"]


def test_build_spare_set_uses_remaining_engineering_capacity_after_chassis_work():
    state = create_state()
    state.player_team.factory_size = 5
    state.finance.balance = 500_000
    state.player_spares = 0
    state.player_construction_projects = [
        PlayerConstructionProject(
            active=True,
            scope="next_year",
            name="1999 Chassis",
            allocation_percent=80,
            assigned_engineers=43,
        )
    ]
    logger = Mock()

    result = handle_build_spare_set(state, logger)

    assert result["status"] == "success"
    assert result["data"]["engineering_required_percentage"] == 9
    assert result["data"]["construction_usage_percent_before"] == 80
    assert result["data"]["construction_usage_percent_after"] == 89
    assert result["data"]["spare_construction_usage_percent_after"] == 9
