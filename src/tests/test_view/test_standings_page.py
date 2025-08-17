import sys
import types
import pandas as pd
import flet as ft
import pytest

# --- Map local modules to the package paths standings_page expects ---
import pw_view.custom_widgets.custom_container as _local_custom_container
import pw_view.custom_widgets.custom_datatable as _local_custom_datatable
import pw_view.custom_widgets.results_table_multi as _local_results_table_multi

sys.modules.setdefault("pw_view", types.ModuleType("pw_view"))
sys.modules.setdefault("pw_view.custom_widgets", types.ModuleType("pw_view.custom_widgets"))
sys.modules["pw_view.custom_widgets.custom_container"] = _local_custom_container
sys.modules["pw_view.custom_widgets.custom_datatable"] = _local_custom_datatable
sys.modules["pw_view.custom_widgets.results_table_multi"] = _local_results_table_multi

# Import after aliasing so it picks up the right modules
import pw_view.standings_page as sp


# --- Minimal fakes for view/controller/app ---

class FakeDriverPageController:
    def __init__(self):
        self.last_driver = None

    def go_to_driver_page(self, name: str):
        self.last_driver = name


class FakeController:
    def __init__(self):
        self.driver_page_controller = FakeDriverPageController()


class FakeMainApp:
    def __init__(self):
        self.update_calls = 0
        self.views = []
        self.overlay = []

    def update(self):
        self.update_calls += 1


class FakeView:
    def __init__(self):
        self.controller = FakeController()
        self.main_app = FakeMainApp()

        # Provide what's used by StandingsPage / widgets
        self.page_header_style = ft.TextThemeStyle.DISPLAY_MEDIUM
        self.background_image = ft.Container()  # any control is fine

        # Paths are only concatenated into strings; files needn’t exist for unit tests
        self.flags_small_path = r"C:\fake\flags_small"
        self.team_logos_path = r"C:\fake\team_logos"
        self.sponsor_logos_path = r"C:\fake\sponsor_logos"
        self.dark_grey = "#23232A"


# --- Fixtures ---

@pytest.fixture
def view():
    return FakeView()


@pytest.fixture
def drivers_df():
    return pd.DataFrame(
        [
            ["GB", "Lewis Hamilton", "Mercedes", 200],
            ["NL", "Max Verstappen", "Red Bull", 220],
        ],
        columns=["Flag", "Driver", "Team", "Pts"],
    )


@pytest.fixture
def constructors_df():
    # model uses 0-based Rnd; page adds +1
    return pd.DataFrame(
        [
            ["DE", "Mercedes", 0, 350],
            ["AT", "Red Bull", 1, 360],
        ],
        columns=["Flag", "Team", "Rnd", "Pts"],
    )


@pytest.fixture
def flags_drivers():
    return ["GB", "NL"]


@pytest.fixture
def flags_teams():
    return ["DE", "AT"]


@pytest.fixture
def race_data():
    race_countries = ["Bahrain", "SaudiArabia", "Australia"]
    driver_results = [
        ["Lewis Hamilton", 3, 2, 1],
        ["Max Verstappen", 1, 1, 2],
    ]
    return race_countries, driver_results


# --- Tests ---

def test_initial_layout_has_header_and_tabs(view):
    page = sp.StandingsPage(view)

    # Header
    assert isinstance(page.controls[0], ft.Text)
    assert page.controls[0].value == "Standings"

    # Background stack + Tabs
    assert isinstance(page.controls[1], ft.Stack)
    tabs = page.controls[1].controls[1]
    assert isinstance(tabs, ft.Tabs)
    assert [t.text for t in tabs.tabs] == ["Drivers", "Constructors", "Results"]
    assert tabs.selected_index == 0


def test_update_standings_populates_all_three_tables(view, drivers_df, constructors_df,
                                                     flags_drivers, flags_teams, race_data):
    race_countries, driver_results = race_data
    page = sp.StandingsPage(view)

    page.update_standings(
        drivers_df,
        constructors_df,
        flags_drivers,
        flags_teams,
        driver_results,
        race_countries,
    )

    # Drivers table
    assert page.drivers_table is not None
    assert page.drivers_tab.content.content == page.drivers_table.list_view
    # first row first cell should be a DataCell with a Row(Image, Text)
    first_cell = page.drivers_table.data_table.rows[0].cells[0]
    assert isinstance(first_cell, ft.DataCell)

    # Constructors table: Rnd incremented for display
    assert page.constructors_table is not None
    displayed_rows = page.constructors_table.data_table.rows

    displayed_rnds = [row.cells[2].content.value for row in displayed_rows]
    assert displayed_rnds == [1, 2]

    # Results table: columns = 1 driver col + races, rows = drivers
    assert page.results_table is not None
    assert len(page.results_table.data_table.columns) == 1 + len(race_countries)
    assert len(page.results_table.data_table.rows) == len(driver_results)

    # Tabs reset & app updated
    assert page.tabs.selected_index == 0
    assert view.main_app.update_calls >= 1


def test_clicking_driver_name_navigates(view, drivers_df, constructors_df,
                                        flags_drivers, flags_teams, race_data):
    race_countries, driver_results = race_data
    page = sp.StandingsPage(view)
    page.update_standings(
        drivers_df,
        constructors_df,
        flags_drivers,
        flags_teams,
        driver_results,
        race_countries,
    )

    # Simulate clicking the first row, first column cell (Flag+Name cell)
    cell = page.drivers_table.data_table.rows[1].cells[0]  # Max Verstappen row
    # Build a minimal event that Flet would pass
    event = types.SimpleNamespace(control=cell)
    # The callback was assigned by update_standings
    assert callable(cell.on_tap)
    cell.on_tap(event)

    assert view.controller.driver_page_controller.last_driver == "NL"


def test_extract_text_handles_nested_controls(view):
    page = sp.StandingsPage(view)
    nested = ft.Container(
        content=ft.Row(
            controls=[ft.Text("Hidden"), ft.Column(controls=[ft.Text("Visible Driver")])]
        )
    )
    # _extract_text returns the first text it finds
    got = page._extract_text(nested)
    assert got in {"Hidden", "Visible Driver"}
