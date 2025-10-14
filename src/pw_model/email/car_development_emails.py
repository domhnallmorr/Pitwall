import random

def car_development_started_email(development_type: str, time_left: int, cost: int) -> str:
    messages = [
        f"Development of the {development_type} upgrade has begun. It will be completed in {time_left} weeks. The cost of the upgrade is ${cost:,}.",
        f"The team has started work on the {development_type} upgrade. It will be completed in {time_left} weeks. The cost of the upgrade is ${cost:,}.",
        f"Development of the {development_type} upgrade is now underway. It will be completed in {time_left} weeks. The cost of the upgrade is ${cost:,}.",
    ]

    return add_link_text_to_car_development_email(random.choice(messages))

def car_development_completed_email(development_type: str, speed_increase: int) -> str:
    messages = [
        f"The {development_type} upgrade has been completed. The car's speed has increased by {speed_increase} units.",
        f"The team has successfully completed the {development_type} upgrade. The car's speed has increased by {speed_increase} units.",
        f"The {development_type} upgrade is now complete. The car's speed has increased by {speed_increase} units.",
    ]

    return random.choice(messages)

def ai_development_completed_email(car_development_updates: list[list[str]]) -> str:
    if len(car_development_updates) == 0:
        return "There are no car development updates to report."
    else:
        message = "See below for car development updates:\n\n"
        for update in car_development_updates:
            message += f"{update[0]} has completed a {update[1]} upgrade.\n"
    
        return add_link_text_to_car_development_email(message)
    
def add_link_text_to_car_development_email(message: str) -> str:
    return message + "\n\nSee link below for the car comparison page to see the current pecking order of the grid."