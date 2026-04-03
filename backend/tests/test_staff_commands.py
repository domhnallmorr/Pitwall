from unittest.mock import Mock, patch

from app.commands.staff_commands import (
    handle_get_technical_director_replacement_candidates,
    handle_get_manager_replacement_candidates,
    handle_get_tyre_supplier_replacement_candidates,
    handle_get_title_sponsor_replacement_candidates,
    handle_get_replacement_candidates,
    handle_replace_commercial_manager,
    handle_replace_technical_director,
    handle_replace_tyre_supplier,
    handle_replace_title_sponsor,
    handle_replace_driver,
    handle_repair_car_wear,
    handle_start_car_development,
    handle_update_workforce,
)
from app.models.calendar import Calendar, Event, EventType
from app.models.commercial_manager import CommercialManager
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team
from app.models.technical_director import TechnicalDirector
from app.models.title_sponsor import TitleSponsor
from app.models.tyre_supplier import TyreSupplier


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2, workforce=120, car_wear=10, title_sponsor_name="Windale", title_sponsor_yearly=32_500_000, title_sponsor_contract_length=1, tyre_supplier_name="Greatday", tyre_supplier_deal="partner", tyre_supplier_contract_length=1)],
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
        tyre_suppliers=[
            TyreSupplier(id=41, name="Greatday", country="USA", wear=60, grip=80, start_year=0),
            TyreSupplier(id=42, name="Spanrock", country="Japan", wear=80, grip=70, start_year=0),
        ],
        calendar=Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=10),
        circuits=[],
        player_team_id=1,
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


def test_start_car_development_validates_and_handles_errors():
    state = create_state()
    logger = Mock()
    assert handle_start_car_development(state, logger, development_type=None)["status"] == "error"

    with patch("app.commands.staff_commands.PlayerCarDevelopmentManager.start", side_effect=ValueError("invalid")):
        result = handle_start_car_development(state, logger, development_type="minor")
    assert result["status"] == "error"
    assert result["message"] == "invalid"

    with patch("app.commands.staff_commands.PlayerCarDevelopmentManager.start", side_effect=RuntimeError("x")):
        result = handle_start_car_development(state, logger, development_type="minor")
    assert result["status"] == "error"
    assert result["message"] == "x"


def test_repair_car_wear_validates_edge_cases_and_exceptions():
    state = create_state()
    logger = Mock()
    state.player_team_id = None
    assert handle_repair_car_wear(state, logger, wear_points=10)["status"] == "error"

    state = create_state()
    state.player_team.car_wear = 0
    assert handle_repair_car_wear(state, logger, wear_points=10)["status"] == "error"
    assert handle_repair_car_wear(state, logger, wear_points=None)["status"] == "error"
    assert handle_repair_car_wear(state, logger, wear_points=0)["status"] == "error"

    # Force int conversion failure to hit generic exception path.
    state.player_team.car_wear = "bad"
    result = handle_repair_car_wear(state, logger, wear_points=1)
    assert result["status"] == "error"
    assert logger.error.called


def test_update_workforce_validates_edge_cases_and_exceptions():
    state = create_state()
    logger = Mock()
    state.player_team_id = None
    assert handle_update_workforce(state, logger, workforce=100)["status"] == "error"

    state = create_state()
    assert handle_update_workforce(state, logger, workforce=None)["status"] == "error"
    assert handle_update_workforce(state, logger, workforce=-1)["status"] == "error"
    assert handle_update_workforce(state, logger, workforce=251)["status"] == "error"

    result = handle_update_workforce(state, logger, workforce="oops")
    assert result["status"] == "error"
    assert logger.error.called
