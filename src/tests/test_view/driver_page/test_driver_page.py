import pytest
import pandas as pd
from unittest.mock import MagicMock

# Import the module under test. Adjust the import paths if needed.
from pw_view.driver_page.driver_page import DriverPage
from pw_controller.driver_page.driver_page_data import DriverPageData

# --- Dummies for all the custom widgets & view dependencies ---

class DummyRating:
    def __init__(self, *args, **kwargs):
        self.updated = None
    def update_row(self, value):
        self.updated = value

class DummyResultsTable:
    def __init__(self, view):
        self.view = view
        self.list_view = "dummy_list_view"
        self.updated_args = None
    def update_results(self, countries, results):
        self.updated_args = (countries, results)

class DummyContainer:
    def __init__(self, *args, **kwargs):
        pass

class DummyHeader:
    def __init__(self, *args, **kwargs):
        pass

class DummyMainApp:
    def __init__(self):
        self.updated = False
    def update(self):
        self.updated = True

class DummyView:
    def __init__(self):
        # anything you like here
        self.page_header_style = "HEADER_STYLE"
        self.SUBHEADER_FONT_SIZE = 14
        self.driver_images_path = "/foo/bar"
        self.background_image = "BG_IMG"
        self.main_app = DummyMainApp()

# Automatically patch your custom widgets at import-time
@pytest.fixture(autouse=True)
def patch_widgets(monkeypatch):
    from pw_view.driver_page import driver_page
    monkeypatch.setattr(driver_page, "RatingWidget", DummyRating)
    monkeypatch.setattr(driver_page, "DriverResultsTable", DummyResultsTable)
    monkeypatch.setattr(driver_page, "CustomContainer", DummyContainer)
    monkeypatch.setattr(driver_page, "HeaderContainer", DummyHeader)

def test_update_page_populates_everything():
    view = DummyView()
    page = DriverPage(view)

    # Build a tiny DataFrame with one row of dummy race results
    df = pd.DataFrame([[11, 22, 33]], columns=["r1", "r2", "r3"])

    data = DriverPageData(
        name="TestDriver",
        age=30,
        country="Narnia",
        salary=2_000_000,
        contract_length=1,
        retiring=False,
        starts=50,
        championships=1,
        wins=5,
        speed=4,
        consistency=2,
        qualifying=5,
        race_results_df=df,
        qualy_results_df=df,
        race_countries=["UK", "DE", "FR"],
    )

    page.update_page(data)

    # Personal details
    assert page.name_text.value == "Name: TestDriver"
    assert page.age_text.value == "Age: 30 Years"
    assert page.country_text.value == "Country: Narnia"
    # Image path lowercases the name
    assert page.image.src.endswith("testdriver.png")

    # Career stats
    assert page.starts_text.value == "Starts: 50"
    assert page.championships_text.value == "Championships: 1"
    assert page.wins_text.value == "Wins: 5"

    # Contract
    assert page.salary_text.value == "Salary: $2,000,000"
    assert page.contract_length_text.value == "Contract Length: 1 Year(s)"
    assert page.contract_status_text.value == "Contract Status: Contract Expiring"

    # Ratings widgets
    assert page.ability_widget.updated == 4
    assert page.speed_widget.updated == 4
    assert page.qualifying_widget.updated == 5
    assert page.consistency_widget.updated == 2

    # Results table got the right data
    assert page.results_table.updated_args == (["UK", "DE", "FR"], [11, 22, 33])

    # And finally we call through to main_app.update()
    assert view.main_app.updated
