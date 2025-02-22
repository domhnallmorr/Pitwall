import pytest
from pw_model.finance.damage_costs import DamageCosts

# Create a fake randomiser that always returns a fixed value.
class FakeDamageRandomiser:
    def calculate_random_cost(self, ranges):
        # For testing, return the minimum cost of the first range (50,000).
        return ranges[0][0]

@pytest.fixture
def fixed_costs():
    # Create a DamageCosts instance and replace its randomiser with our fake one.
    dc = DamageCosts()
    dc.randomiser = FakeDamageRandomiser()
    return dc

def test_one_driver_crash(fixed_costs):
    # Only driver 1 crashes.
    fixed_costs.calculate_race_damage_costs(player_driver1_crashed=True, player_driver2_crashed=False)
    # With our fake randomiser, the crash cost should be 50_000.
    assert fixed_costs.driver1_latest_crash_cost == 50_000
    assert fixed_costs.driver2_latest_crash_cost == 0
    # The race cost should be the sum of both drivers' costs.
    assert fixed_costs.damage_costs[-1] == 50_000
    # Season total should update accordingly.
    assert fixed_costs.damage_costs_this_season == 50_000

def test_other_driver_crash(fixed_costs):
    # Only driver 2 crashes.
    fixed_costs.calculate_race_damage_costs(player_driver1_crashed=False, player_driver2_crashed=True)
    # With our fake randomiser, the crash cost should be 50_000.
    assert fixed_costs.driver1_latest_crash_cost == 0
    assert fixed_costs.driver2_latest_crash_cost == 50_000
    assert fixed_costs.damage_costs[-1] == 50_000
    assert fixed_costs.damage_costs_this_season == 50_000

def test_both_drivers_crash(fixed_costs):
    # Both drivers crash.
    fixed_costs.calculate_race_damage_costs(player_driver1_crashed=True, player_driver2_crashed=True)
    # Each driver incurs 50_000 so the total for the race should be 100_000.
    assert fixed_costs.driver1_latest_crash_cost == 50_000
    assert fixed_costs.driver2_latest_crash_cost == 50_000
    assert fixed_costs.damage_costs[-1] == 100_000
    assert fixed_costs.damage_costs_this_season == 100_000

def test_multiple_races_accumulate_costs(fixed_costs):
    # First race: only driver 1 crashes.
    fixed_costs.calculate_race_damage_costs(player_driver1_crashed=True, player_driver2_crashed=False)
    # Second race: only driver 2 crashes.
    fixed_costs.calculate_race_damage_costs(player_driver1_crashed=False, player_driver2_crashed=True)
    # Third race: both drivers crash.
    fixed_costs.calculate_race_damage_costs(player_driver1_crashed=True, player_driver2_crashed=True)
    
    # Check individual race costs.
    assert fixed_costs.damage_costs[0] == 50_000      # Race 1
    assert fixed_costs.damage_costs[1] == 50_000      # Race 2
    assert fixed_costs.damage_costs[2] == 100_000     # Race 3
    # Total cost for the season should be the sum of the above.
    assert fixed_costs.damage_costs_this_season == 200_000
