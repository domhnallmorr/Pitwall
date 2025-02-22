import random
from pw_model.driver.driver_model import DriverModel
from pw_model.team.team_model import TeamModel

def driver_retirement(driver: DriverModel) -> str:
	retirement_messages = [
        f"{driver.name} has announced that this season will be their last on the track, retiring at the age of {driver.age}.",
        f"After a long and successful career, {driver.name} will retire at the end of this season, finishing up at {driver.age} years old.",
        f"This season marks the end of {driver.name}'s illustrious career, as they prepare to retire at the age of {driver.age}.",
        f"At {driver.age}, {driver.name} has decided that this season will be their final one in racing. Retirement awaits at the season's end!",
    ]

    # Choose a random retirement message from the list
	selected_message = random.choice(retirement_messages)
    
	return selected_message

def driver_hiring_email(team: TeamModel, driver: DriverModel) -> str:
    hiring_messages = [
        f"{driver.name} has joined forces with {team.name} for the next season.",
        f"{team.name} has announced the signing of {driver.name} as their new driver.",
        f"{driver.name} joins the ranks of {team.name} as their newest driver!",
    ]

    # Choose a random hiring message from the list
    selected_message = random.choice(hiring_messages)
    
    return selected_message

def manager_hiring_email(team: str, manager: str, role: str) -> str:
     hiring_messages = [
          f"{team} have announced the signing of {manager} as their new {role.lower()} for next season"
     ]

     return random.choice(hiring_messages)

def prize_money_email(prize_money: int) -> str:
    messages = [
        f"Prize money from last season has been confirmed at ${prize_money: ,}. Payments will be made on a weekly basis.",
    ]

    # Choose a random hiring message from the list
    selected_message = random.choice(messages)
    
    return selected_message

def car_update_email() -> str:
    messages = [
         "This years car is ready to hit the track! Check out the car page to see how we stack up against the opposition",
    ]
    
    selected_message = random.choice(messages)
    
    return selected_message

def upgrade_facility(team: TeamModel, facility: str ="factory") -> str:
	messages = [
		f"Exciting news! {team.name} has completed an upgrade to their {facility}.",
		f"{team.name} is investing in excellence with the latest upgrade to their {facility}.",
		f"Attention all fans! {team.name} has improved their {facility} to enhance performance.",
		f"Breaking news: {team.name} unveils an upgraded {facility} to stay at the forefront of F1 technology.",  
		]
    
	return random.choice(messages)

def upgrade_player_facility(facility: str="factory") -> str:
    messages = [
          f"Upgrades to the {facility} have been completed. We should see the benfits in next years car."  
    ]
      
    return random.choice(messages)

def sponsor_income_update_email(sponsorship: int) -> str:
    messages = [
            f"Sponsorship for the upcoming seaosn has been confirmed as ${sponsorship :,}."  
    ]
      
    return random.choice(messages)

def race_financial_summary_email(transport_cost: int, damage_cost: int, title_sponsor_payment: int, profit: int) -> str:
    loss_or_profit = "loss"
    if profit >= 0:
          loss_or_profit = "profit"

    lines = [
                f"We made a {loss_or_profit} of ${profit :,} on the last race. See summary below:\n\n",
                f"Transport Costs: ${transport_cost :,}\n"
                f"Crash Damage Costs: ${damage_cost :,}\n"
                f"Title Sponsor Payment: ${title_sponsor_payment :,}\n"
                f"Total Profit: ${profit :,}\n"
    ]
    
    message = "".join(lines)
    
    return message
