import pytest
from unittest.mock import Mock
from flet import Text, Row, Column, Stack
from pw_view.finance_page.finance_page import FinancePage

class MockView:
    def __init__(self):
        self.background_image = Mock()
        self.page_header_style = Mock()
        self.dark_grey = "#23232A"

@pytest.fixture
def finance_page():
    # Mock the view and create an instance of FinancePage
    view = MockView()
    return FinancePage(view)

def test_initialization(finance_page):
    # Test if the page initializes correctly with the required widgets
    assert isinstance(finance_page, Column)
    assert len(finance_page.controls) == 2
    assert isinstance(finance_page.controls[0], Text)  # "Finance" header
    assert isinstance(finance_page.controls[1], Stack)  # Background stack

def test_setup_widgets(finance_page):
    # Check if widgets are set up correctly
    assert isinstance(finance_page.sponsor_income_text, Text)
    assert finance_page.sponsor_income_text.value == "Sponsorship: $1"

    assert isinstance(finance_page.total_income_text, Text)
    assert finance_page.total_income_text.value == "Total: $1"

    assert isinstance(finance_page.total_expenditure_text, Text)
    assert finance_page.total_expenditure_text.value == "Total: $1"

def test_update_page(finance_page):
    # Test updating the page with mocked FinanceData
    mock_data = {
        "total_sponsorship": 500000,
        "prize_money": 250000,
        "drivers_payments": 100000,
        "total_income": 850000,
        "total_staff_costs_per_year": 300000,
        "drivers_salary": 200000,
        "technical_director_salary": 150000,
        "commercial_manager_salary": 120000,
        "race_costs": 50000,
        "damage_costs": 80000,
        "total_expenditure": 700000,
        "balance_history_dates": ["2023-01-01", "2023-02-01"],
        "balance_history": [500000, 850000],
        "profit": 430_002,
        "title_sponsor": "Some Sponsor",
        "title_sponsor_value": 20_000_000,
        "other_sponsorship": 12_000_050,
        "car_development_costs": 100_000
    }

    finance_page.update_page(mock_data)

    assert finance_page.prize_money_income_text.value == "Prize Money: $250,000"
    assert finance_page.total_income_text.value == "Total: $850,000"
    assert finance_page.total_expenditure_text.value == "Total: $700,000 (To Date)"
    assert finance_page.profit_text.value == "Profit/Loss This Season: $430,002"
    assert finance_page.title_sponsor_text.value == "Title Sponsor: Some Sponsor"
    assert finance_page.title_sponsor_value_text.value == "Title Sponsorship: $20,000,000"
    assert finance_page.sponsor_income_text.value == "Other Sponsorship: $12,000,050"
    assert finance_page.car_development_costs_text.value == "Car Development Costs: $100,000 (To Date)"

    # Simulate chart update (no direct visual assertions, but ensure no errors)
    finance_page.update_history_chart(mock_data)

def test_balance_formatter(finance_page):
    # Test the custom balance formatter
    assert finance_page.balance_formatter(900000, 0) == "$900K"
    assert finance_page.balance_formatter(1500000, 0) == "$1M"
