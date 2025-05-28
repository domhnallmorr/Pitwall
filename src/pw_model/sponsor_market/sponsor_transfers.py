from __future__ import annotations
import logging
import random
from typing import TYPE_CHECKING
from pw_model.pw_model_enums import SponsorTypes

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def get_free_agents(model: Model, for_player_team: bool=False) -> list[str]:
	free_agents: list[str] = []

	for sponsor in model.sponsors:
		if sponsor.retiring is False:
			# TODO when player is applying for sponsor, handle this differently, as per staff market
			if not model.sponsor_market.sponsors_next_year_df.isin([sponsor.name]).any().any():
					free_agents.append(sponsor.name)

	return free_agents

def determine_sponsor_transfers(model: Model) -> None:
	sponsor_market = model.sponsor_market
	
	teams_requiring_title_sponsor = sponsor_market.compile_teams_requiring_sponsor(SponsorTypes.TITLE)

	for team in teams_requiring_title_sponsor:
		free_agents = get_free_agents(model)

		assert len(free_agents) > 0, "Ran out of title sponsors"

		team_sign_sponsor(model, team, SponsorTypes.TITLE, free_agents)

def team_sign_sponsor(model: Model, team: str, sponsor_type: SponsorTypes, free_agents: list[str]) -> None:
	team_model = model.entity_manager.get_team_model(team)
	
	logging.debug(f"{team} hiring {sponsor_type}")
	logging.debug(f"Free Agents: {free_agents}")

	sponsor_signed = random.choice(free_agents)
	model.sponsor_market.handle_team_signing_sponsor(team, sponsor_type, sponsor_signed)