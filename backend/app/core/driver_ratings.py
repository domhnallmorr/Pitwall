def calculate_driver_overall_rating(speed: int | float | None, consistency: int | float | None) -> int:
    speed_value = max(0, min(100, int(speed or 0)))
    consistency_value = max(0, min(100, int(consistency or 0)))
    return max(1, min(100, round((speed_value * 0.75) + (consistency_value * 0.25))))
