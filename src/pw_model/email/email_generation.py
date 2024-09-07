import random

def driver_retirement(driver):
	retirement_messages = [
        f"{driver.name} has announced that this season will be their last on the track, retiring at the age of {driver.age}.",
        f"After a long and successful career, {driver.name} will retire at the end of this season, finishing up at {driver.age} years old.",
        f"This season marks the end of {driver.name}'s illustrious career, as they prepare to retire at the age of {driver.age}.",
        f"At {driver.age}, {driver.name} has decided that this season will be their final one in racing. Retirement awaits at the season's end!",
    ]

    # Choose a random retirement message from the list
	selected_message = random.choice(retirement_messages)
    
	return selected_message

def driver_hiring_email(team, driver):
    hiring_messages = [
        f"{driver.name} has joined forces with {team.name} for the next season.",
        f"{team.name} has announced the signing of {driver.name} as their new driver.",
        f"{driver.name} joins the ranks of {team.name} as their newest driver!",
    ]

    # Choose a random hiring message from the list
    selected_message = random.choice(hiring_messages)
    
    return selected_message