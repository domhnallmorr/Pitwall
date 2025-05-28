import pytest
import flet as ft
from pw_view.finance_page.finance_page import FinancePage

# Dummy tab class to intercept calls
class DummyTab:
    def __init__(self, view):
        self.view = view
        self.updated_with = None

    def update_tab(self, data):
        self.updated_with = data

# Dummy main_app with an update spy
class DummyMainApp:
    def __init__(self):
        self.update_calls = 0

    def update(self):
        self.update_calls += 1

# Dummy view to pass into FinancePage
class DummyView:
    def __init__(self):
        self.background_image = object()
        self.page_header_style = "dummy_style"
        self.main_app = DummyMainApp()

@pytest.fixture(autouse=True)
def patch_tabs(monkeypatch):
    import pw_view.finance_page.finance_page as finance_page_mod
    monkeypatch.setattr(finance_page_mod, 'OverviewTab', DummyTab)
    monkeypatch.setattr(finance_page_mod, 'SponsorsTab', DummyTab)


def test_tabs_initialization():
    view = DummyView()
    page = FinancePage(view)

    assert isinstance(page.tabs, ft.Tabs)
    tabs_list = page.tabs.tabs
    assert len(tabs_list) == 2

    overview_tab, sponsors_tab = tabs_list
    assert overview_tab.text == "Overview"
    assert overview_tab.icon == ft.Icons.BUSINESS
    assert isinstance(overview_tab.content.content, DummyTab)

    assert sponsors_tab.text == "Sponsors"
    assert sponsors_tab.icon == ft.Icons.CASES
    assert isinstance(sponsors_tab.content.content, DummyTab)

def test_background_stack_and_controls():
    view = DummyView()
    page = FinancePage(view)

    # Verify background stack composition
    assert page.background_stack.controls[0] == view.background_image
    assert page.background_stack.controls[1] == page.tabs

    # Verify top-level controls in the Column
    text_control = page.controls[0]
    assert isinstance(text_control, ft.Text)
    assert text_control.value == "Finance"
    assert text_control.theme_style == view.page_header_style
    assert page.controls[1] == page.background_stack

def test_update_page_calls_update_tab_and_main_app_update():
    view = DummyView()
    page = FinancePage(view)
    dummy_data = {}  # TypedDict content not used by DummyTab

    page.update_page(dummy_data)

    assert page.overview_tab.updated_with == dummy_data
    assert page.sponsors_tab.updated_with == dummy_data
    assert view.main_app.update_calls == 1
