import pytest
from unittest.mock import MagicMock, PropertyMock
from pw_model.driver_negotiation.driver_interest import determine_driver_interest, DriverInterest, DriverRejectionReason
from pw_model.driver_negotiation.driver_negotiation_enums import DriverCategory

@pytest.mark.parametrize(
    "driver_name, is_top_5, is_bottom_5_team, rating, starts, age, current_salary, offered_salary, expected_interest, expected_reason",
    [
        # 1) Top 5 driver, player's team is in worst 5 => Not interested (Team Rating)
        ("Lewis Hamilton", True, True, 95, 50, 31, 15_000_000, 20_000_000,
         DriverInterest.NOT_INTERESTED, DriverRejectionReason.TEAM_RATING),
        
        # 2) Non-top-5 driver, player's team not in worst 5, but offered < salary expectation => Not interested (Salary)
        #   rating=70 & starts=30 => classification=TOP => 14M cap
        #   age=26 => +20% => 1.2 * current_salary => 1.2 * 10,000,000 = 12,000,000 => well below the 14M cap
        #   offered=11,000,000 => < expectation => NOT_INTERESTED
        ("Esteban Ocon", False, False, 70, 30, 26, 10_000_000, 11_000_000,
         DriverInterest.NOT_INTERESTED, DriverRejectionReason.SALARY_OFFER),

        # 3) Non-top-5 driver, player's team not in worst 5, offered >= expectation => Accepted
        #   rating=50 & starts=16 => classification=MID => 6M cap
        #   age=24 => +10% => 1.1 * current_salary => 1.1 * 4M = 4.4M => offered=5M => >= 4.4 => ACCEPTED
        ("Lando Norris", False, False, 50, 16, 24, 4_000_000, 5_000_000,
         DriverInterest.ACCEPTED, DriverRejectionReason.NONE),

        # 4) Another example: older ELITE driver, not in worst 5 team, big salary
        #   rating=90 & starts=50 => classification=ELITE => 29M cap
        #   age=35 => +0% => expects exactly current_salary => offered < current => not interested
        ("Fernando Alonso", False, False, 90, 50, 35, 20_000_000, 18_000_000,
         DriverInterest.NOT_INTERESTED, DriverRejectionReason.SALARY_OFFER),
    ],
)
def test_determine_driver_interest(
    driver_name,
    is_top_5,
    is_bottom_5_team,
    rating,
    starts,
    age,
    current_salary,
    offered_salary,
    expected_interest,
    expected_reason
):
    """
    This test verifies that 'determine_driver_interest' respects:
      - The team rating constraint (top-5 drivers won't go to bottom-5 teams).
      - The driver's salary expectation.
    """

    ####
    # 1) Mock model.season fields (drivers_by_rating, teams_by_rating)
    ####
    mock_season = MagicMock()
    
    # If is_top_5 is True, we put driver_name in the top 5 drivers list
    mock_season.drivers_by_rating = []
    top_5_driver_data = [("DriverInTop5_" + str(i), 99 - i) for i in range(5)]
    if is_top_5:
        # Replace the first of the top 5 with this driver's name
        top_5_driver_data[0] = (driver_name, 95)
    mock_season.drivers_by_rating = top_5_driver_data + [("OtherDriver", 80)]
    
    # If is_bottom_5_team is True, then we ensure the player's team is in the last 5
    # We'll create 10 example teams, and place the player's team either in top or bottom 5
    all_teams = []
    for i in range(10):
        all_teams.append((f"Team_{i}", 90 - (i * 5)))
    if is_bottom_5_team:
        # Move the player's team to last position in the list
        all_teams[-1] = ("PlayerTeam", 30)
    else:
        # Move the player's team to somewhere in the top 5
        all_teams[0] = ("PlayerTeam", 95)
    mock_season.teams_by_rating = all_teams

    ####
    # 2) Mock the driver_model (overall_rating, career_stats, age, contract)
    ####
    mock_driver_model = MagicMock()
    type(mock_driver_model).overall_rating = PropertyMock(return_value=rating)
    mock_driver_model.career_stats.starts = starts
    mock_driver_model.age = age
    mock_driver_model.contract.salary = current_salary

    ####
    # 3) Mock the main model
    ####
    mock_model = MagicMock()
    mock_model.season = mock_season
    # The player's team is "PlayerTeam" in our data above
    mock_model.player_team = "PlayerTeam"
    # Return our mocked driver_model for the given driver_name
    mock_model.get_driver_model.return_value = mock_driver_model

    ####
    # 4) Call function under test
    ####
    interest, reason = determine_driver_interest(mock_model, driver_name, offered_salary)

    ####
    # 5) Assertions
    ####
    assert interest == expected_interest, (
        f"For driver='{driver_name}' with rating={rating}, age={age}, "
        f"and offered={offered_salary}, expected interest={expected_interest} but got {interest}."
    )
    assert reason == expected_reason, (
        f"For driver='{driver_name}' with rating={rating}, age={age}, "
        f"and offered={offered_salary}, expected reason={expected_reason} but got {reason}."
    )
