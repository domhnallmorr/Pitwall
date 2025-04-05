from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from race_weekend_model.grand_prix_model import GrandPrixModel

from race_weekend_model.race_model_enums import ParticipantStatus

def post_race_actions(grand_prix_model: GrandPrixModel):
	update_driver_stats(grand_prix_model)


def update_driver_stats(grand_prix_model: GrandPrixModel):
	standings_model = grand_prix_model.standings_model

	for idx, row in standings_model.dataframe.iterrows():
		driver = row["Driver"]
		participant = grand_prix_model.race_weekend_model.get_particpant_model_by_name(driver)
		driver_model = participant.driver
		
		# career stats
		driver_model.career_stats.update_after_race()

		# season stats
		participant.driver.season_stats.starts_this_season += 1
		
		if idx == 0: # update wins
			driver_model.season_stats.wins_this_season += 1
			driver_model.team_model.season_stats.wins_this_season += 1
		if idx in [0, 1, 2]: # podiums
			driver_model.season_stats.podiums_this_season += 1
			driver_model.team_model.season_stats.podiums_this_season += 1
		if row["Status"] == ParticipantStatus.RETIRED:
			driver_model.season_stats.dnfs_this_season += 1
			driver_model.team_model.season_stats.dnfs_this_season += 1
