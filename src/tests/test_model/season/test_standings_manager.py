
import pytest

import pandas as pd

from pw_model.season import standings_manager

from tests import create_model

def test_create_standings_dataframe():

	teams = {
		"Warrick": ["Jacques Villeneuve", "Heinz-Harald Frentzen"],
		"Ferano": ["Michael Schumacher", "Eddie Irvine"],
		"McAlister": ["Mika Hakkinen", "David Coulthard"],
	}

	drivers_standings_df, constructors_standings_df = standings_manager.create_standings_dataframe(teams)

	assert drivers_standings_df.columns.tolist() == ["Driver", "Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs", "Starts"]

	expected = [
		["Jacques Villeneuve", "Warrick", 0, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Warrick", 0, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferano", 0, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferano", 0, 0, 0, 0, 0, 0],
		["Mika Hakkinen", "McAlister", 0, 0, 0, 0, 0, 0],
		["David Coulthard", "McAlister", 0, 0, 0, 0, 0, 0],
		]
	
	assert drivers_standings_df.values.tolist() == expected

	assert constructors_standings_df.columns.tolist() == ["Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs", "Best Result", "Rnd"]

	expected = [
			["Warrick", 0, 0, 0, 0, 0, None, None],
			["Ferano", 0, 0, 0, 0, 0,  None, None],
			["McAlister", 0, 0, 0, 0, 0, None, None],
		]
	
	assert constructors_standings_df.values.tolist() == expected

def test_standings_manager_setup():
	model = create_model.create_model()
	standings_manager_instance = standings_manager.StandingsManager(model)

	expected = [
		["Jacques Villeneuve", "Warrick", 0, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Warrick", 0, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferano", 0, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferano", 0, 0, 0, 0, 0, 0],
		["Giancarlo Fisichella", "Benedetti", 0, 0, 0, 0, 0, 0],
		["Alexander Wurz", "Benedetti", 0, 0, 0, 0, 0, 0],
		["Mika Hakkinen", "McAlister", 0, 0, 0, 0, 0, 0],
		["David Coulthard", "McAlister", 0, 0, 0, 0, 0, 0],
		]

	assert standings_manager_instance.drivers_standings_df.head(8).values.tolist() == expected

	expected = [
			["Warrick", 0, 0, 0, 0, 0,  None, None],
			["Ferano", 0, 0, 0, 0, 0,  None, None],
			["Benedetti", 0, 0, 0, 0, 0,  None, None],
			["McAlister", 0, 0, 0, 0, 0,  None, None],
		]
	
	assert standings_manager_instance.constructors_standings_df.head(4).values.tolist() == expected

def test_update_standings():
	model = create_model.create_model()
	standings_manager_instance = standings_manager.StandingsManager(model)

	columns = ["Driver"]
	data = ["Mika Hakkinen", "David Coulthard", "Eddie Irvine", "Michael Schumacher", "Jacques Villeneuve", "Heinz-Harald Frentzen", "Giancarlo Fisichella", "Alexander Wurz"]
	result1 = pd.DataFrame(columns=columns, data=data)
	
	result1["Position"] = [i + 1 for i in range(len(data))]
	result1["Team"] = ["McAlister", "McAlister", "Ferano", "Ferano", "Warrick", "Warrick", "Benedetti", "Benedetti"]

	standings_manager_instance.update_standings(result1)

	expected = [
		["Mika Hakkinen", "McAlister", 10, 0, 0, 0, 0, 0],
		["David Coulthard", "McAlister", 6, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferano", 4, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferano", 3, 0, 0, 0, 0, 0],
		["Jacques Villeneuve", "Warrick", 2, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Warrick", 1, 0, 0, 0, 0, 0],
		# ["Giancarlo Fisichella", "Benedetti", 0, 0, 0, 0, 0, 0],
		# ["Alexander Wurz", "Benedetti", 0, 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.drivers_standings_df.head(6).values.tolist() == expected

	model.season.calendar.next_race_idx += 1
	data = ["Michael Schumacher", "Eddie Irvine", "Mika Hakkinen", "Jacques Villeneuve", "David Coulthard", "Heinz-Harald Frentzen", "Giancarlo Fisichella", "Alexander Wurz"]
	result2 = pd.DataFrame(columns=columns, data=data)
	result2["Position"] = [i + 1 for i in range(len(data))]
	result2["Team"] = ["Ferano", "Ferano", "McAlister", "Warrick", "McAlister", "Warrick", "Benedetti", "Benedetti"]

	standings_manager_instance.update_standings(result2)

	expected = [
		["Mika Hakkinen", "McAlister", 14, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferano", 13, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferano", 10, 0, 0, 0, 0, 0],
		["David Coulthard", "McAlister", 8, 0, 0, 0, 0, 0],
		["Jacques Villeneuve", "Warrick", 5, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Warrick", 2, 0, 0, 0, 0, 0],
		# ["Giancarlo Fisichella", "Benedetti", 0, 0, 0, 0, 0, 0],
		# ["Alexander Wurz", "Benedetti", 0, 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.drivers_standings_df.head(6).values.tolist() == expected

	expected = [
			["Ferano", 23, 0, 0, 0, 0, 1, 1],
			["McAlister", 22, 0, 0, 0, 0, 1, 0],
			["Warrick", 7, 0, 0, 0, 0, 4, 1],
			# ["Arrows", 0, 0, 0, 0, 0],
			# ["Benedetti", 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.constructors_standings_df.head(3).values.tolist() == expected

	#TODO test stats such as starts, DNFs in standings df

def test_team_position():
	# test the functions for returning the position of a team in the standings
	# NOTE positions are 0 indexed
	model = create_model.create_model(mode="headless")

	model.player_team = "Warrick"
	assert model.season.standings_manager.player_team_position == 0

	model.player_team = "Marchetti"
	assert model.season.standings_manager.player_team_position == 10

	assert model.season.standings_manager.team_position("Ferano") == 1
