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

def manager_hiring_email(team, manager, role):
     hiring_messages = [
          f"{team} have announced the signing of {manager} as thier new {role.lower()} for next season"
     ]

     return random.choice(hiring_messages)

def prize_money_email(prize_money):
    messages = [
        f"Prize money from last season has been confirmed at ${prize_money: ,}. Payments will be made on a weekly basis.",
    ]

    # Choose a random hiring message from the list
    selected_message = random.choice(messages)
    
    return selected_message

def car_update_email():
    messages = [
         "This years car is ready to hit the track! Check out the car page to see how we stack up against the opposition",
    ]
    
    selected_message = random.choice(messages)
    
    return selected_message

def upgrade_facility(team, facility="factory"):
	messages = [
		f"Exciting news! {team.name} has completed an upgrade to their {facility}.",
		f"{team.name} is investing in excellence with the latest upgrade to their {facility}.",
		f"Attention all fans! {team.name} has improved their {facility} to enhance performance.",
		f"Breaking news: {team.name} unveils an upgraded {facility} to stay at the forefront of F1 technology.",  
		]
    
	return random.choice(messages)

def upgrade_player_facility(facility="factory"):
    messages = [
          f"Upgrades to the {facility} have been completed. We should see the benfits in next years car."  
    ]
      
    return random.choice(messages)

def sponsor_income_update_email(sponsorship):
    messages = [
            f"Sponsorship for the upcoming seaosn has been confirmed as ${sponsorship :,}."  
    ]
      
    return random.choice(messages)