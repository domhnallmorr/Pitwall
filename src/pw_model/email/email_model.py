from __future__ import annotations
import collections
from typing import TYPE_CHECKING

import pandas as pd

from pw_model.driver.driver_model import DriverModel
from pw_model.senior_staff.technical_director import TechnicalDirector
from pw_model.team.team_model import TeamModel
from pw_model.email import email_generation
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	
class Email:
	def __init__(self, subject: str, message: str, sender: str=""):
		self.subject = subject
		self.message = message
		self.status = "unread"
		self.sender = sender


class Inbox:
	def __init__(self, model: Model):
		self.model = model

		self.reset_number_new_emails()
		self.setup_email_list()

		welcome_email = Email("Welcome", "Welcome to Pitwall!", sender="The Board")
		self.add_email(welcome_email)


	# @property
	# def number_unread(self):
	# 	unread = 0

	# 	for email in self.emails:
	# 		if email.status == "unread":
	# 			unread += 1

	# 	return unread

	def reset_number_new_emails(self) -> None:
		self.new_emails = 0

	def add_email(self, email: Email) -> None:
		self.emails.appendleft(email)
		self.new_emails += 1

	def setup_email_list(self) -> None:
		self.emails: collections.deque[Email] = collections.deque(maxlen=20)

	def generate_driver_retirement_email(self, driver: DriverModel) -> None:
		msg = email_generation.driver_retirement(driver)
		email = Email(f"{driver.name} retiring!", msg)

		self.add_email(email)

	def generate_driver_hiring_email(self, team: TeamModel, driver: DriverModel) -> None:
		msg = email_generation.driver_hiring_email(team, driver)

		email = Email(f"{team.name} have hired {driver.name}!", msg)
		self.add_email(email)

	def generate_facility_update_email(self, team: TeamModel) -> None:
		msg = email_generation.upgrade_facility(team)

		email = Email(f"{team.name} have upgraded their factory!", msg)
		self.add_email(email)

	def generate_player_facility_update_email(self) -> None:
		msg = email_generation.upgrade_player_facility()

		email = Email(f"Factory has been upgraded!", msg)
		self.add_email(email)

	#TODO remove this method, use manager_hired instead
	def new_technical_director_email(self, team: TeamModel, technical_director: TechnicalDirector) -> None:
		msg = email_generation.hire_technical_director_email(team, technical_director)

		email = Email(f"New TD: {team.name} have hired {technical_director.name}!", msg)
		self.add_email(email)

	def new_sponsor_income_email(self, sponsorship: int) -> None:
		msg = email_generation.sponsor_income_update_email(sponsorship)

		email = Email(f"Sponsor Income Update", msg)
		self.add_email(email)

	def new_prize_money_email(self, prize_money: int) -> None:
		msg = email_generation.prize_money_email(prize_money)

		email = Email(f"Prize Money Confirmed", msg)
		self.add_email(email)

	def new_car_update_email(self) -> None:
		msg = email_generation.car_update_email()

		email = Email(f"New Car Ready", msg)
		self.add_email(email)
	
	def new_manager_hired_email(self, team: str, manager: str, role: str) -> None:
		msg = email_generation.manager_hiring_email(team, manager, role)

		email = Email(f"{team} hire {manager}", msg)
		self.add_email(email)

	def new_transport_cost_email(self, cost: int) -> None:
		msg = email_generation.transport_costs_email(cost)

		email = Email(f"Transport Costs", msg)
		self.add_email(email)

	def generate_dataframe(self) -> pd.DataFrame:
		data = []

		for email in self.emails:
			data.append([email.subject, email.message, email.sender])

		return pd.DataFrame(columns=["Subject", "Message", "Sender"], data=data)
	
	def load_dataframe(self, df: pd.DataFrame) -> None:
		self.emails.clear()

		for idx, row in df.iterrows():

			subject = row["Subject"]
			message = row["Message"]
			sender = row["Sender"]

			email = Email(subject, message, sender)

			self.add_email(email)
