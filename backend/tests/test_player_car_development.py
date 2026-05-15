from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.player_construction import PlayerConstructionManager
from app.models.calendar import Calendar, Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState, PlayerConstructionProject
from app.models.team import Team
from app.models.technical_director import TechnicalDirector


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[
            Team(
                id=1,
                name="Warrick",
                country="United Kingdom",
                car_speed=80,
                facilities=70,
                workforce=182,
                design_staff=63,
                engineering_staff=61,
                mechanics_staff=58,
            )
        ],
        drivers=[],
        technical_directors=[TechnicalDirector(id=1, name="Peter Heed", age=45, skill=80, team_id=1)],
        calendar=Calendar(events=[Event(name="Race 1", week=2, type=EventType.RACE)], current_week=1),
        circuits=[],
        player_team_id=1,
    )


def test_start_creates_stage_based_active_project():
    state = create_state()
    manager = PlayerCarDevelopmentManager()

    project = manager.start(state, "current_year")

    assert project.active is True
    assert project.scope == "current_year"
    assert project.name == "Current Chassis Upgrade"
    assert project.current_stage_index == 0
    assert [stage.key for stage in project.stages] == ["design", "cfd", "model", "wind_tunnel"]
    assert project.allocation_percent == 100
    assert project.assigned_designers == 63
    assert project.weekly_cost == 0


def test_process_week_fills_current_stage_without_charging_development_cost():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")

    state.calendar.current_week = 2
    result = manager.process_week(state)

    assert result["status"] == "processed"
    assert result["projects"][0]["status"] == "in_progress"
    assert result["projects"][0]["stage"] == "Design"
    assert state.player_car_development.stages[0].progress == 1
    assert state.player_car_development.progress_carry > 0
    assert state.player_car_development.paid == 0
    assert state.finance.transactions == []


def test_can_split_designers_between_current_and_next_year_projects():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    current = manager.start(state, "current_year")
    manager.set_allocation(state, "current_year", 60)
    next_year = manager.start(state, "next_year")

    assert current.allocation_percent == 60
    assert current.assigned_designers == 38
    assert next_year.allocation_percent == 40
    assert next_year.assigned_designers == 25

    payload = manager.get_payload(state)
    assert payload["projects"]["current_year"]["available_allocation_percent"] == 60
    assert payload["projects"]["next_year"]["available_allocation_percent"] == 40

    result = manager.process_week(state)

    assert len(result["projects"]) == 2
    assert state.player_car_development.stages[0].progress == 0
    assert state.player_next_year_car_development.stages[0].progress == 0
    assert state.player_car_development.progress_carry > state.player_next_year_car_development.progress_carry


def test_low_resource_team_can_take_multiple_weeks_to_fill_one_bar():
    state = create_state()
    state.player_team.design_staff = 20
    state.player_team.facilities = 18
    state.technical_directors[0].skill = 39
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")

    results = [manager.process_week(state) for _ in range(4)]
    fifth_week = manager.process_week(state)

    assert all(result["projects"][0]["status"] == "blocked" for result in results)
    assert fifth_week["projects"][0]["status"] == "in_progress"
    assert state.player_car_development.stages[0].progress == 1


def test_allocation_cannot_exceed_remaining_design_staff_percent():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    manager.set_allocation(state, "current_year", 70)
    manager.start(state, "next_year")

    try:
        manager.set_allocation(state, "next_year", 40)
    except ValueError as exc:
        assert "exceeds 100%" in str(exc)
    else:
        raise AssertionError("Expected allocation validation error")


def test_finish_stage_can_advance_early_and_final_stage_creates_construction_project():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")

    for expected_stage_index in [0, 1, 2, 3]:
        state.player_car_development.stages[expected_stage_index].progress = 1
        manager.finish_current_stage(state)

    project = state.player_car_development
    assert project.active is False
    assert project.completed is True
    assert project.quality_score > 0
    assert project.speed_delta == 1
    assert state.player_team.car_speed == 80
    assert len(state.player_construction_projects) == 1
    assert state.player_construction_projects[0].scope == "current_year"
    assert state.player_construction_projects[0].active is False
    assert state.player_construction_projects[0].speed_delta == 1
    assert state.player_construction_projects[0].total_cost == 20_000
    assert state.player_construction_projects[0].design_blocks == 4


def test_full_stage_autocompletes_during_weekly_processing():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    state.player_car_development.stages[0].progress = 9

    result = manager.process_week(state)

    assert result["projects"][0]["completed_stages"][0]["stage"] == "Design"
    assert state.player_car_development.stages[0].completed is True
    assert state.player_car_development.current_stage_index == 1


def test_completed_current_year_project_resets_for_next_upgrade_payload():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    for stage in state.player_car_development.stages:
        stage.progress = 10
        manager.finish_current_stage(state)

    payload = manager.get_payload(state)

    assert state.player_car_development is None
    assert payload["projects"]["current_year"]["active"] is False
    assert payload["projects"]["current_year"]["completed"] is False


def test_full_stage_progress_produces_better_upgrade():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    for stage in state.player_car_development.stages:
        stage.progress = 10
        manager.finish_current_stage(state)

    assert state.player_car_development.speed_delta == 7
    assert state.player_team.car_speed == 80
    assert state.player_construction_projects[0].speed_delta == 7
    assert state.player_construction_projects[0].total_cost == 300_000
    assert state.player_construction_projects[0].design_blocks == 40


def test_next_year_project_completion_does_not_apply_until_rollover():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "next_year")
    for stage in state.player_next_year_car_development.stages:
        stage.progress = 10
        manager.finish_current_stage(state, "next_year")

    assert state.player_next_year_car_development.completed is True
    assert state.player_next_year_car_development.speed_delta == 7
    assert state.player_team.car_speed == 80
    assert state.player_construction_projects[0].scope == "next_year"
    assert state.player_construction_projects[0].total_cost == 500_000
    assert state.player_construction_projects[0].units_required == 1


def test_next_year_construction_builds_one_chassis_at_a_time():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "next_year")
    for stage in state.player_next_year_car_development.stages:
        stage.progress = 10
        manager.finish_current_stage(state, "next_year")

    construction_manager = PlayerConstructionManager()
    first = construction_manager.start_project(state, "next_year")
    first.progress = first.progress_required - 1
    first.progress_carry = 1

    construction_manager.process_week(state)

    assert first.completed is True
    assert first.units_built == 1
    payload = construction_manager.get_payload(state)["projects"]["next_year"]
    assert payload["race_ready_built"] == 1
    assert payload["race_ready_required"] == 2
    assert payload["can_start"] is True

    second = construction_manager.start_project(state, "next_year")

    assert second is not first
    assert second.active is True
    assert second.total_cost == 500_000
    assert second.units_required == 1


def test_current_year_construction_completion_applies_speed_gain_and_costs():
    state = create_state()
    state.player_setup_knowledge = 80
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    for stage in state.player_car_development.stages:
        stage.progress = 10
        manager.finish_current_stage(state)

    construction = state.player_construction_projects[0]
    PlayerConstructionManager().start_project(state, "current_year")
    construction.progress = construction.progress_required - 1
    construction.progress_carry = 1

    result = PlayerConstructionManager().process_week(state)

    assert result["projects"][0]["status"] == "completed"
    assert construction.completed is True
    assert construction.applied is True
    assert state.player_team.car_speed == 87
    assert state.player_setup_knowledge == 38
    assert construction.paid > 0
    assert any(tx.category == TransactionCategory.CONSTRUCTION for tx in state.finance.transactions)
    assert any("Setup knowledge: 80 -> 38" in email.body for email in state.emails)


def test_current_year_upgrade_setup_reduction_clamps_to_minimum():
    state = create_state()
    state.player_setup_knowledge = 10
    project = PlayerConstructionProject(
        active=True,
        scope="current_year",
        name="Large Upgrade",
        speed_delta=4,
        paid=120_000,
        quality_score=40,
    )

    PlayerConstructionManager()._apply_current_year_upgrade(state, project)

    assert state.player_team.car_speed == 84
    assert state.player_setup_knowledge == 1
    assert project.applied is True


def test_chassis_construction_allocation_respects_spare_work_used_this_week():
    state = create_state()
    state.player_construction_usage_percent = 30
    state.player_construction_usage_week = state.calendar.current_week
    state.player_construction_usage_year = state.year
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    for stage in state.player_car_development.stages:
        stage.progress = 1
        manager.finish_current_stage(state)

    construction = PlayerConstructionManager().start_project(state, "current_year")

    assert construction.allocation_percent == 70
    try:
        PlayerConstructionManager().set_allocation(state, "current_year", 80)
    except ValueError as exc:
        assert "70% is available" in str(exc)
    else:
        raise AssertionError("Expected allocation validation error")


def test_construction_estimates_follow_resource_and_upgrade_size_ranges():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "current_year")
    for stage in state.player_car_development.stages:
        stage.progress = 1
        manager.finish_current_stage(state)
    PlayerConstructionManager().start_project(state, "current_year")

    minor_payload = PlayerConstructionManager().get_payload(state)["projects"]["current_year"]
    assert 2 <= minor_payload["estimated_weeks"] <= 4

    state = create_state()
    manager.start(state, "next_year")
    for stage in state.player_next_year_car_development.stages:
        stage.progress = 10
        manager.finish_current_stage(state, "next_year")
    PlayerConstructionManager().start_project(state, "next_year")

    next_payload = PlayerConstructionManager().get_payload(state)["projects"]["next_year"]
    assert 4 <= next_payload["estimated_weeks"] <= 8
