from app.main import HealthCheck

def test_health_check_model():
    health = HealthCheck(status="OK", version="1.0.0")
    assert health.status == "OK"
    assert health.version == "1.0.0"
