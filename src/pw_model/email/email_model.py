import collections

from pw_model.email import email_generation

class Email:
	def __init__(self, subject, message, sender=""):
		self.subject = subject
		self.message = message
		self.status = "unread"
		self.sender = sender


class Inbox:
	def __init__(self, model):
		self.model = model

		self.setup_email_list()

		welcome_email = Email("Welcome", "Welcome to Pitwall!", sender="The Board")
		self.add_email(welcome_email)


	@property
	def number_unread(self):
		unread = 0

		for email in self.emails:
			if email.status == "unread":
				unread += 1

		return unread

	def add_email(self, email):
		self.emails.appendleft(email)

	def setup_email_list(self):
		self.emails = collections.deque(maxlen=20)

	def generate_driver_retirement_email(self, driver):
		msg = email_generation.driver_retirement(driver)
		email = Email(f"{driver.name} retiring!", msg)

		self.add_email(email)

	def generate_driver_hiring_email(self, team, driver):
		msg = email_generation.driver_hiring_email(team, driver)

		email = Email(f"{team.name} have hired {driver.name}!", msg)
		self.add_email(email)

	def generate_facility_update_email(self, team):
		msg = email_generation.upgrade_facility(team)

		email = Email(f"{team.name} have upgraded their factory!", msg)
		self.add_email(email)

	def generate_player_facility_update_email(self):
		msg = email_generation.upgrade_player_facility()

		email = Email(f"Factory has been upgraded!", msg)
		self.add_email(email)

	def new_technical_director_email(self, team, technical_director):
		msg = email_generation.hire_technical_director_email(team, technical_director)

		email = Email(f"New TD: {team.name} have hired {technical_director.name}!", msg)
		self.add_email(email)

	def new_sponsor_income_email(self, team):
		msg = email_generation.sponsor_income_update_email(team)

		email = Email(f"Sponsor Income Update", msg)
		self.add_email(email)

	def new_prize_money_email(self, prize_money):
		msg = email_generation.prize_money_email(prize_money)

		email = Email(f"Prize Money Confirmed", msg)
		self.add_email(email)

	def new_car_update_email(self):
		msg = email_generation.car_update_email()

		email = Email(f"New Car Ready", msg)
		self.add_email(email)