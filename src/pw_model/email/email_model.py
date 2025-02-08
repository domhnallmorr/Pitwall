from __future__ import annotations
import collections
from typing import TYPE_CHECKING
from enum import Enum

import pandas as pd

from pw_model.driver.driver_model import DriverModel
from pw_model.senior_staff.technical_director import TechnicalDirector
from pw_model.team.team_model import TeamModel
from pw_model.email import email_generation
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	
class EmailStatusEnums(Enum):
	READ = "read"
	UNREAD = "unread"

class Email:
	def __init__(self, subject: str, message: str, email_id: int,  status: EmailStatusEnums, sender: str=""):
		self.subject = subject
		self.message = message
		self.status = status
		self.sender = sender
		self.email_id = email_id

class Inbox:
	def __init__(self, model: Model):
		self.model = model
		self.new_email_id = 0

		self.reset_number_new_emails()
		self.setup_email_list()

		msg = "Welcome to Pitwall!"
		title = "Welcome"
		sender = "The board"

		self.add_email(msg, title, sender=sender)

	def reset_number_new_emails(self) -> None:
		self.new_emails = 0

	def add_email(self, msg: str, title: str, sender: str="", status: EmailStatusEnums=EmailStatusEnums.UNREAD) -> None:
		email = Email(title, msg, self.new_email_id, status=status)
		self.emails.appendleft(email)
		self.new_emails += 1
		self.new_email_id += 1

	def mark_email_as_read(self, email_id: int) -> None:
		for email in self.emails:
			if email.email_id == email_id:
				email.status = EmailStatusEnums.READ

	def setup_email_list(self) -> None:
		self.emails: collections.deque[Email] = collections.deque(maxlen=20)

	def generate_driver_retirement_email(self, driver: DriverModel) -> None:
		msg = email_generation.driver_retirement(driver)
		title = f"{driver.name} retiring!"
		self.add_email(msg, title)

	def generate_driver_hiring_email(self, team: TeamModel, driver: DriverModel) -> None:
		msg = email_generation.driver_hiring_email(team, driver)
		title = f"{team.name} have hired {driver.name}!"
		self.add_email(msg, title)

	def generate_facility_update_email(self, team: TeamModel) -> None:
		msg = email_generation.upgrade_facility(team)
		title = f"{team.name} have upgraded their factory!"
		self.add_email(msg, title)

	def generate_player_facility_update_email(self) -> None:
		msg = email_generation.upgrade_player_facility()
		title = f"Factory has been upgraded!"
		self.add_email(msg, title)

	#TODO remove this method, use manager_hired instead
	def new_technical_director_email(self, team: TeamModel, technical_director: TechnicalDirector) -> None:
		msg = email_generation.hire_technical_director_email(team, technical_director)
		title = f"New TD: {team.name} have hired {technical_director.name}!"
		self.add_email(msg, title)

	def new_sponsor_income_email(self, sponsorship: int) -> None:
		msg = email_generation.sponsor_income_update_email(sponsorship)
		title = f"Sponsor Income Update"
		self.add_email(msg, title)

	def new_prize_money_email(self, prize_money: int) -> None:
		msg = email_generation.prize_money_email(prize_money)
		title = f"Prize Money Confirmed"
		self.add_email(msg, title)

	def new_car_update_email(self) -> None:
		msg = email_generation.car_update_email()
		title = f"New Car Ready"
		self.add_email(msg, title)
	
	def new_manager_hired_email(self, team: str, manager: str, role: str) -> None:
		msg = email_generation.manager_hiring_email(team, manager, role)
		title = f"{team} hire {manager}"
		self.add_email(msg, title)

	def new_race_finance_email(self, transport_cost: int, title_sponsor_payment: int, profit: int) -> None:
		msg = email_generation.race_financial_summary_email(transport_cost, title_sponsor_payment, profit)
		title = f"Race Financial Summary"
		self.add_email(msg, title)

	def generate_dataframe(self) -> pd.DataFrame:
		data = []

		for email in self.emails:
			data.append([email.subject, email.message, email.sender, email.status.value])

		data.reverse()
		return pd.DataFrame(columns=["Subject", "Message", "Sender", "Status"], data=data)
	
	def load_dataframe(self, df: pd.DataFrame) -> None:
		self.emails.clear()

		self.new_email_id = 0

		for idx, row in df.iterrows():

			subject = row["Subject"]
			message = row["Message"]
			sender = row["Sender"]
			status = row["Status"]
			self.add_email(message, subject, sender=sender, status=EmailStatusEnums(status))

