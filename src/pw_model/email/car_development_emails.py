import random

def car_development_started_email(development_type: str, time_left: int, cost: int) -> str:
    messages = [
        f"Development of the {development_type} upgrade has begun. It will be completed in {time_left} weeks. The cost of the upgrade is ${cost:,}.",
        f"The team has started work on the {development_type} upgrade. It will be completed in {time_left} weeks. The cost of the upgrade is ${cost:,}.",
        f"Development of the {development_type} upgrade is now underway. It will be completed in {time_left} weeks. The cost of the upgrade is ${cost:,}.",
    ]

    return random.choice(messages)

def car_development_completed_email(development_type: str, speed_increase: int) -> str:
    messages = [
        f"The {development_type} upgrade has been completed. The car's speed has increased by {speed_increase} units.",
        f"The team has successfully completed the {development_type} upgrade. The car's speed has increased by {speed_increase} units.",
        f"The {development_type} upgrade is now complete. The car's speed has increased by {speed_increase} units.",
    ]

    return random.choice(messages)

def ai_development_completed_email(development_type: str, team: str) -> str:
    messages = [
        f"{team} have announced the completion of their {development_type} upgrade.",
        f"{team} have completed their {development_type} upgrade.",
        f"{team} have successfully implemented their {development_type} upgrade.",
    ]
    
    return random.choice(messages)