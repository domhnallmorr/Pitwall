from __future__ import annotations
import random
from typing import TYPE_CHECKING

import pandas as pd

from pw_model.pw_model_enums import SponsorTypes
from pw_model.sponsor_market import sponsor_transfers

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


class SponsorMarket:
	def __init__(self, model: Model):
		self.model = model

		self.FINAL_WEEK_ANNOUNCE = min(40, model.FINAL_WEEK - 1)

	@property
	def player_requiring_title_sponsor(self) -> bool:
		if self.model.player_team in self.compile_teams_requiring_sponsor(SponsorTypes.TITLE):
			return True
		else:
			return False

	def setup_dataframes(self) -> None:
		columns = ["Team", "WeekToAnnounce", "SponsorType", "Sponsor", "Payment", "ContractLength"]
		self.new_contracts_df = pd.DataFrame(columns=columns) # dataframe for tracking details of new contracts offered to new hires

		columns  = ["Team", SponsorTypes.TITLE.value]

		this_year_data = [] # sponsors for upcoming season
		next_year_data = [] # sponsors for next year

		for team in self.model.teams:
			title_sponsor = team.finance_model.sponsorship_model.title_sponsor
			title_sponsor_model = self.model.entity_manager.get_sponsor_model(title_sponsor)

			this_year_data.append([team.name, title_sponsor_model.name])

			if title_sponsor_model.contract.contract_length < 2:
				next_year_data.append([team.name, None])
			else:
				next_year_data.append([team.name, title_sponsor_model.name])
			
		self.sponsors_this_year_df = pd.DataFrame(columns=columns, data=this_year_data)
		self.sponsors_next_year_df = pd.DataFrame(columns=columns, data=next_year_data)

		'''
		create dataframe for next year, this gets populated as the season progresses and signings are announced
		'''
		self.sponsors_next_year_announced_df = self.sponsors_next_year_df.copy(deep=True)
	
	def compute_transfers(self) -> None:
		sponsor_transfers.determine_sponsor_transfers(self.model)

	def compile_teams_requiring_sponsor(self, sponsor_type: SponsorTypes) -> list[str]:
		teams = []

		for idx, row in self.sponsors_next_year_df.iterrows():
			if row[sponsor_type.value] is None:
				teams.append(row["Team"])
		
		return teams
	
	def handle_team_signing_sponsor(self, team: str, sponsor_type: SponsorTypes, sponsor_signed: str) -> None:
		self.sponsors_next_year_df.loc[self.sponsors_next_year_df["Team"] == team, sponsor_type.value] = sponsor_signed
		week_to_announce = max(random.randint(4, self.FINAL_WEEK_ANNOUNCE), self.model.season.calendar.current_week + 1) # ensure the week is not in the past
		self.new_contracts_df.loc[len(self.new_contracts_df.index)] = [team, week_to_announce, sponsor_type.value, sponsor_signed, 4_000_000, random.randint(2, 5)]

	def announce_signings(self) -> None:
		for idx, row in self.new_contracts_df.iterrows():
			if row["WeekToAnnounce"] == self.model.season.calendar.current_week:
				sponsor_hired = row["Sponsor"]
				team_name = row["Team"]
				role = SponsorTypes(row["SponsorType"]) # role is stored as an enum value (string) in the DF
				
				self.complete_hiring(sponsor_hired, team_name, role)

	def complete_hiring(self, sponsor_signed: str, team_name: str, sponsor_type: SponsorTypes, payment: int=None) -> None:	
		team_model = self.model.entity_manager.get_team_model(team_name)
		
		# self.sponsors_next_year_df.loc[self.sponsors_next_year_df["team"] == team_name, sponsor_type.value] = sponsor_signed
		self.sponsors_next_year_announced_df.loc[self.sponsors_next_year_df["Team"] == team_name, sponsor_type.value] = sponsor_signed
		self.model.inbox.new_sponsor_signed_email(sponsor_signed, team_name, sponsor_type.value)

	def update_team_sponsors(self) -> None:
		assert None not in self.sponsors_next_year_df.values
		print(self.sponsors_next_year_df)
		for idx, row in self.sponsors_next_year_df.iterrows():
			team_name = row["Team"]
			sponsor_name = row[SponsorTypes.TITLE.value]

			if sponsor_name in self.new_contracts_df["Sponsor"].values:
				team_model = self.model.entity_manager.get_team_model(team_name)

				team_model.finance_model.sponsorship_model.title_sponsor = row[SponsorTypes.TITLE.value]
				contract = self.new_contracts_df.loc[self.new_contracts_df["Sponsor"] == row[SponsorTypes.TITLE.value]].to_dict(orient="records")[0]
				print(team_model.name)
			
				team_model.finance_model.sponsorship_model.title_sponsor_model.contract.total_payment = contract["Payment"]
				team_model.finance_model.sponsorship_model.title_sponsor_model.contract.contract_length = contract["ContractLength"]