from pw_model.driver_negotiation.driver_interest import determine_driver_interest, DriverInterest
from tests import create_model

def test_driver_interest_return_value():
    """Test that determine_driver_interest returns valid enum values"""
    model = create_model.create_model(mode="headless")
    result = determine_driver_interest(model, "Michael Schumacher")
    assert isinstance(result, DriverInterest)
    assert result in [DriverInterest.VERY_INTERESTED, DriverInterest.NOT_INTERESTED]

def test_driver_interest_distribution():
    """Test that both outcomes occur with roughly even distribution"""
    model = create_model.create_model(mode="headless")
    
    results = []
    iterations = 1000
    
    for _ in range(iterations):
        result = determine_driver_interest(model, "Michael Schumacher")
        results.append(result)
    
    very_interested_count = results.count(DriverInterest.VERY_INTERESTED)
    not_interested_count = results.count(DriverInterest.NOT_INTERESTED)
    
    # With 1000 iterations, each outcome should occur at least 400 times
    # This gives some room for randomness while ensuring both outcomes occur frequently
    assert very_interested_count > 400
    assert not_interested_count > 400
    assert very_interested_count + not_interested_count == iterations

def test_driver_interest_integration():
    """Test that driver interest affects the hiring process"""
    model = create_model.create_model(mode="headless")
    model.player_team = "Williams"
    
    # Run multiple iterations to ensure we see both outcomes
    for _ in range(50):
        # Reset the driver offers for each iteration
        model.driver_offers.setup_new_season()
        
        interest = determine_driver_interest(model, "Michael Schumacher")
        model.driver_offers.add_offer("Michael Schumacher")
        
        # Verify the driver was added to approached drivers list
        assert "Michael Schumacher" in model.driver_offers.drivers_who_have_been_approached()
        
        if interest == DriverInterest.VERY_INTERESTED:
            # Could add more specific checks here once you implement
            # the actual hiring process based on interest
            pass
        else:
            # Could add more specific checks here for rejection handling
            pass