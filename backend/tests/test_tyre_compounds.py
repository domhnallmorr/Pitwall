import random

from app.core.tyre_compounds import TyreCompoundManager
from app.models.calendar import Calendar
from app.models.state import GameState
from app.models.team import Team
from app.models.tyre_supplier import TyreSupplier


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom")],
        drivers=[],
        tyre_suppliers=[
            TyreSupplier(id=1, name="Greatday", country="USA", wear=60, grip=80, resources=88, innovation=82, reliability=90),
            TyreSupplier(id=2, name="Spanrock", country="Japan", wear=80, grip=70, resources=86, innovation=91, reliability=84),
        ],
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
    )


def test_generate_for_new_career_creates_three_dry_compounds_per_supplier():
    state = create_state()

    TyreCompoundManager().generate_for_new_career(state, rng=random.Random(7))

    assert set(state.season_tyre_compounds.keys()) == {"Greatday", "Spanrock"}
    assert [compound.name for compound in state.season_tyre_compounds["Greatday"]] == ["Hard", "Medium", "Soft"]
    assert all(compound.year == 1998 for compound in state.season_tyre_compounds["Spanrock"])


def test_generate_for_new_career_reflects_supplier_profiles():
    soft_grip_gap_total = 0
    hard_wear_gap_total = 0
    medium_stiffness_gap_total = 0

    for seed in range(100):
        state = create_state()
        TyreCompoundManager().generate_for_new_career(state, rng=random.Random(seed))

        greatday = {compound.name: compound for compound in state.season_tyre_compounds["Greatday"]}
        spanrock = {compound.name: compound for compound in state.season_tyre_compounds["Spanrock"]}

        soft_grip_gap_total += spanrock["Soft"].grip - greatday["Soft"].grip
        hard_wear_gap_total += greatday["Hard"].wear - spanrock["Hard"].wear
        medium_stiffness_gap_total += greatday["Medium"].stiffness - spanrock["Medium"].stiffness

    assert soft_grip_gap_total > 0
    assert hard_wear_gap_total > 0
    assert medium_stiffness_gap_total > 0
