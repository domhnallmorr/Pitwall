from pathlib import Path
from unittest.mock import patch

from app.core.save_manager import save_game, load_game, has_save
from app.models.email import Email, EmailCategory
from app.models.finance import Finance, TransactionCategory
from app.models.state import GameState
from app.models.calendar import Calendar
from app.models.team import Team
from app.models.driver import Driver
from app.models.team_principal import TeamPrincipal
from app.models.technical_director import TechnicalDirector
from app.models.commercial_manager import CommercialManager


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[
            Team(
                id=1,
                name="Warrick",
                country="United Kingdom",
                driver1_id=1,
                driver2_id=2,
                team_principal_id=10,
                technical_director_id=20,
                commercial_manager_id=30,
                car_speed=80,
                title_sponsor_name="Windale",
                title_sponsor_contract_length=2,
            )
        ],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, speed=84, race_starts=33, wins=11),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, speed=72, race_starts=65, wins=1),
        ],
        team_principals=[
            TeamPrincipal(
                id=10,
                name="Franklin Warrick",
                country="United Kingdom",
                age=56,
                skill=80,
                contract_length=99,
                team_id=1,
                owns_team=True,
            )
        ],
        technical_directors=[
            TechnicalDirector(
                id=20,
                name="Peter Heed",
                country="United Kingdom",
                age=52,
                skill=78,
                contract_length=3,
                salary=250_000,
                team_id=1,
            )
        ],
        commercial_managers=[
            CommercialManager(
                id=30,
                name="Jace Whitman",
                country="United States",
                age=45,
                skill=73,
                contract_length=2,
                salary=180_000,
                team_id=1,
            )
        ],
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        player_team_id=1,
        emails=[
            Email(
                id=1,
                sender="Competition Office",
                subject="Test Email",
                body="Hello",
                week=1,
                year=1998,
                category=EmailCategory.GENERAL,
            )
        ],
        next_email_id=2,
        finance=Finance(balance=10_000_000),
        grid_snapshots={
            1998: [
                {
                    "Team": "Warrick",
                    "Driver1": "John Newhouse",
                    "Driver2": "Henrik Friedrich",
                    "TeamPrincipal": "Franklin Warrick",
                    "TechnicalDirector": "Peter Heed",
                    "CommercialManager": "Jace Whitman",
                    "TitleSponsor": "Windale",
                    "TitleSponsorContractLength": 2,
                    "OtherSponsorshipYearly": "5000000",
                }
            ]
        },
        driver_season_results={
            1998: {
                1: [{"event_name": "Australian GP", "position": 1, "points": 10}],
            }
        },
        qualifying_results_by_event={
            "Australian GP": [
                {"position": 1, "driver_id": 1, "driver_name": "John Newhouse", "best_lap_ms": 81234},
            ]
        },
        latest_race_incidents=[
            {"type": "pit_stop", "driver_id": 1, "lap": 21},
        ],
        planned_ai_signings=[
            {"team_id": 2, "seat": "driver1_id", "driver_id": 99, "status": "planned"},
        ],
        announced_ai_signings=[
            {"team_id": 2, "seat": "driver2_id", "driver_id": 98, "status": "announced"},
        ],
        planned_ai_cm_signings=[
            {"team_id": 2, "manager_id": 77, "status": "planned"},
        ],
        announced_ai_cm_signings=[
            {"team_id": 2, "manager_id": 78, "status": "announced"},
        ],
        planned_ai_td_signings=[
            {"team_id": 2, "director_id": 88, "status": "planned"},
        ],
        announced_ai_td_signings=[
            {"team_id": 2, "director_id": 89, "status": "announced"},
        ],
        planned_ai_title_sponsor_signings=[
            {"team_id": 2, "sponsor_name": "Purple", "status": "planned"},
        ],
        announced_ai_title_sponsor_signings=[
            {"team_id": 2, "sponsor_name": "Zenteq", "status": "announced"},
        ],
        planned_ai_car_updates=[
            {"team_id": 2, "week": 7, "delta": 3, "applied": False},
        ],
    )


def test_save_and_load_round_trip(tmp_path: Path):
    state = create_state()
    state.finance.add_transaction(
        week=1,
        year=1998,
        amount=500_000,
        category=TransactionCategory.SPONSORSHIP,
        description="Opening payment",
    )
    save_path = tmp_path / "autosave.json"

    saved = save_game(state, path=str(save_path))
    loaded = load_game(path=str(save_path))

    assert saved == str(save_path)
    assert loaded.year == 1998
    assert loaded.player_team_id == 1
    assert loaded.drivers[0].race_starts == 33
    assert loaded.drivers[0].wins == 11
    assert loaded.team_principals[0].name == "Franklin Warrick"
    assert loaded.technical_directors[0].name == "Peter Heed"
    assert loaded.commercial_managers[0].name == "Jace Whitman"
    assert loaded.grid_snapshots[1998][0]["TitleSponsorContractLength"] == 2
    assert loaded.qualifying_results_by_event["Australian GP"][0]["best_lap_ms"] == 81234
    assert loaded.latest_race_incidents[0]["type"] == "pit_stop"
    assert loaded.planned_ai_td_signings[0]["director_id"] == 88
    assert loaded.announced_ai_title_sponsor_signings[0]["sponsor_name"] == "Zenteq"
    assert loaded.finance.transactions[0].category == TransactionCategory.SPONSORSHIP


def test_has_save_true_and_false(tmp_path: Path):
    state = create_state()
    save_path = tmp_path / "autosave.json"

    assert has_save(path=str(save_path)) is False
    save_game(state, path=str(save_path))
    assert has_save(path=str(save_path)) is True


def test_load_game_accepts_grid_snapshot_rows_with_integer_values(tmp_path: Path):
    state = create_state()
    state.grid_snapshots[1998] = [
        {
            "Team": "Warrick",
            "TitleSponsor": "Windale",
            "TitleSponsorContractLength": 2,
            "OtherSponsorshipYearly": "5000000",
        }
    ]
    save_path = tmp_path / "autosave.json"

    save_game(state, path=str(save_path))
    loaded = load_game(path=str(save_path))

    assert loaded.grid_snapshots[1998][0]["TitleSponsorContractLength"] == 2


@patch("app.core.save_manager.load_team_principals")
def test_load_game_backfills_missing_team_principals_for_legacy_save(mock_load_team_principals, tmp_path: Path):
    state = create_state()
    state.team_principals = []
    state.teams[0].team_principal_id = None
    save_path = tmp_path / "autosave.json"
    save_game(state, path=str(save_path))

    mock_load_team_principals.return_value = [
        TeamPrincipal(
            id=10,
            name="Franklin Warrick",
            country="United Kingdom",
            age=56,
            skill=80,
            contract_length=99,
            team_id=1,
            owns_team=True,
        )
    ]

    loaded = load_game(path=str(save_path))

    assert len(loaded.team_principals) == 1
    assert loaded.team_principals[0].name == "Franklin Warrick"
    assert loaded.team_principals[0].team_id is None
    assert loaded.teams[0].team_principal_id is None
