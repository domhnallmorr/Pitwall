import pytest
from unittest.mock import MagicMock
from pw_view.staff_page.staff_page import StaffPage
from pw_model.pw_model_enums import StaffRoles
from pw_controller.staff_page.staff_page_data import StaffPageData, DriverData, SeniorStaffData, StaffPlayerRequires

@pytest.fixture
def mock_view():
    """Fixture for creating a mocked view."""
    view = MagicMock()
    view.page_header_style = "header_style"
    view.background_image = "mock_background_image"
    view.clicked_button_style = "clicked_button_style"
    view.main_app.update = MagicMock()
    return view

@pytest.fixture
def staff_page(mock_view):
    """Fixture for initializing StaffPage."""
    return StaffPage(view=mock_view)


def test_update_page(staff_page):
    """Test the update_page method with mock data."""
    mock_data = StaffPageData(
        drivers=[
            DriverData(name="Driver 1", age=25, salary=100000, contract_length=2, retiring=False, speed=90,
                       consistency=80, qualifying=5, country="USA", starts=10),
            DriverData(name="Driver 2", age=30, salary=120000, contract_length=1, retiring=True, speed=85,
                       consistency=75, qualifying=2, country="UK", starts=15),
        ],
        technical_director=SeniorStaffData(name="Tech Director", age=50, salary=200000, contract_length=3, skill=95, retiring=True),
        commercial_manager=SeniorStaffData(name="Comm Manager", age=45, salary=150000, contract_length=1, skill=88, retiring=False),
        staff_values=[["Ferrari", 200], ["Williams", 180]],
        
        staff_player_requires = StaffPlayerRequires(
            player_requiring_driver1=False,
            player_requiring_driver2=True,
            player_requiring_commercial_manager=True,
            player_requiring_technical_director=False,
        )
    )

    staff_page.update_page(mock_data)

    # Verify driver data update
    assert staff_page.driver1_container.name_text.value == "Name: Driver 1"
    assert staff_page.driver1_container.age_text.value == "Age: 25 Years"
    assert staff_page.driver1_container.country_text.value == "Country: USA"
    assert staff_page.driver1_container.starts_text.value == "Starts: 10"
    assert staff_page.driver1_container.salary_text.value == "Salary: $100,000"
    assert staff_page.driver1_container.contract_length_text.value == "Contract Length: 2 Year(s)"
    assert staff_page.driver1_container.contract_status_text.value == "Contract Status: Contracted"
    assert staff_page.driver1_container.replace_button.disabled is True

    assert staff_page.driver2_container.name_text.value == "Name: Driver 2"
    assert staff_page.driver2_container.age_text.value == "Age: 30 Years"
    assert staff_page.driver2_container.country_text.value == "Country: UK"
    assert staff_page.driver2_container.starts_text.value == "Starts: 15"
    assert staff_page.driver2_container.salary_text.value == "Salary: $120,000"
    assert staff_page.driver2_container.contract_length_text.value == "Contract Length: 1 Year(s)"
    assert staff_page.driver2_container.contract_status_text.value == "Contract Status: Retiring"
    assert staff_page.driver2_container.replace_button.disabled is False

    # Verify manager data update
    assert staff_page.technical_director_container.name_text.value == "Name: Tech Director"
    assert staff_page.technical_director_container.age_text.value == "Age: 50 Years"
    assert staff_page.technical_director_container.salary_text.value == "Salary: $200,000"
    assert staff_page.technical_director_container.contract_length_text.value == "Contract Length: 3 Year(s)"
    assert staff_page.technical_director_container.contract_status_text.value == "Contract Status: Retiring"
    assert staff_page.technical_director_container.replace_button.disabled is True

    assert staff_page.commercial_manager_container.name_text.value == "Name: Comm Manager"
    assert staff_page.commercial_manager_container.age_text.value == "Age: 45 Years"
    assert staff_page.commercial_manager_container.salary_text.value == "Salary: $150,000"
    assert staff_page.commercial_manager_container.contract_length_text.value == "Contract Length: 1 Year(s)"
    assert staff_page.commercial_manager_container.contract_status_text.value == "Contract Status: Contract Expiring"
    assert staff_page.commercial_manager_container.replace_button.disabled is False

def test_workforce_button(staff_page):
    """Test the enabling/disabling of the workforce hire button."""
    staff_page.disable_hire_workforce_btn()
    assert staff_page.hire_workforce_button.disabled is True

    staff_page.enable_hire_workforce_btn()
    assert staff_page.hire_workforce_button.disabled is False
