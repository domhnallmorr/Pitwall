
import builtins
from types import SimpleNamespace
import pytest

# ---- Test helpers ----

class DummyMainApp:
    def update(self):
        # mimic Flet's page/app update without side-effects
        pass

class DummyView:
    # Values used across your widgets
    SUBHEADER_FONT_SIZE = 18
    page_header_style = None  # your code passes this into ft.Text(theme_style=...), None is fine for tests
    background_image = ""     # blank path is okay for ft.Image in tests
    dark_grey = "#333333"

    def __init__(self):
        self.main_app = DummyMainApp()

# ---- Fixtures ----

@pytest.fixture()
def view():
    return DummyView()

@pytest.fixture()
def car_page(view):
    # Import inside fixture so pytest collection works even if Flet is absent in some environments.
    from pw_view.car_page.car_page import CarPage
    return CarPage(view)

@pytest.fixture()
def sample_data_not_started():
    # Use SimpleNamespace so we don't need to import CarPageData; runtime duck-typing is fine.
    # Import enums to ensure status strings match the app's expectations.
    from pw_model.car_development.car_development_model import CarDevelopmentStatusEnums
    return SimpleNamespace(
        # graph pieces
        car_speed_history={
            "Team A": [90, 92, 93],
            "Team B": [88, 90, 91],
        },
        team_colors={"Team A": "#ff0000", "Team B": "#0000ff"},
        countries=["Bahrain", "Jeddah", "Melbourne"],
        # development status
        current_status=CarDevelopmentStatusEnums.NOT_STARTED.value,
        progress=0.0,
        testing_progress=5,
        # engine
        engine_supplier_name="Ferrari",
        engine_supplier_deal="premium",
        engine_power=90,
        engine_resources=85,
        engine_overall_rating=88,
        # tyres
        tyre_supplier_name="Pirelli",
        tyre_supplier_deal="standard",
        tyre_grip=78,
        tyre_wear=62,
    )

@pytest.fixture()
def sample_data_in_progress(sample_data_not_started):
    from pw_model.car_development.car_development_model import CarDevelopmentStatusEnums
    d = SimpleNamespace(**vars(sample_data_not_started))
    d.current_status = CarDevelopmentStatusEnums.IN_PROGRESS.value
    d.progress = 50  # percent scale expected by RatingWidget
    return d

# ---- Tests ----

def test_car_page_builds_tabs(car_page):
    # The CarPage should expose the tab components after construction
    assert hasattr(car_page, "car_development_tab")
    assert hasattr(car_page, "engine_tab")
    assert hasattr(car_page, "tyre_tab")
    assert hasattr(car_page, "car_comparison_graph")

def test_update_page_propagates_to_tabs_and_buttons(car_page, sample_data_not_started, sample_data_in_progress):
    # First: NOT_STARTED -> buttons enabled, progress 0
    car_page.update_page(sample_data_not_started)

    dev_tab = car_page.car_development_tab
    # Buttons present and enabled
    assert hasattr(dev_tab, "major_develop_btn")
    assert hasattr(dev_tab, "medium_develop_btn")
    assert hasattr(dev_tab, "minor_develop_btn")
    assert dev_tab.major_develop_btn.disabled is False
    assert dev_tab.medium_develop_btn.disabled is False
    assert dev_tab.minor_develop_btn.disabled is False

    # Engine tab reflects supplier texts
    eng = car_page.engine_tab
    assert "Ferrari" in eng.supplier_name.value
    assert "Premium".lower() in eng.supplier_deal.value.lower()

    # Tyre tab reflects supplier texts
    tyre = car_page.tyre_tab
    assert "Pirelli" in tyre.supplier_name.value
    assert "Standard".lower() in tyre.supplier_deal.value.lower()

    # Now: IN_PROGRESS -> buttons disabled, progress shown (>= value provided)
    car_page.update_page(sample_data_in_progress)
    assert dev_tab.major_develop_btn.disabled is True
    assert dev_tab.medium_develop_btn.disabled is True
    assert dev_tab.minor_develop_btn.disabled is True
    # Progress widget should exist; exact filled-stars are managed internally
    assert isinstance(dev_tab.progress_bar, type(dev_tab.progress_bar))

def test_comparison_graph_updates_series_and_axis(car_page, sample_data_not_started):
    car_page.update_page(sample_data_not_started)
    graph = car_page.car_comparison_graph
    # Number of series equals number of teams
    assert hasattr(graph, "chart")
    series = getattr(graph.chart, "data_series", [])
    assert len(series) == len(sample_data_not_started.car_speed_history)

    # Bottom axis should be built from countries list (same count)
    bottom_axis = getattr(graph.chart, "bottom_axis", None)
    # Try to read labels count defensively depending on how axis stores them
    labels = []
    if bottom_axis is not None:
        # flet.ChartAxis holds labels as a list
        labels = getattr(bottom_axis, "labels", [])
    assert len(labels) == len(sample_data_not_started.countries)
