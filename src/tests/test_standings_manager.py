
import pytest

import pandas as pd

from pw_model import pw_model
from pw_model.season import standings_manager

from tests import create_model

# class DummyModel(pw_model.Model):
# 	def __init__(self):
		
# 		self.teams = []

# 		self.teams.append(test_team_functions.gen_dummy_team(model=self, name="Williams", driver1="Jacques Villeneuve", driver2="Heinz-Harald Frentzen")) 
# 		self.teams.append(test_team_functions.gen_dummy_team(model=self, name="Ferrari", driver1="Michael Schumacher", driver2="Eddie Irvine")) 
# 		self.teams.append(test_team_functions.gen_dummy_team(model=self, name="McLaren", driver1="Mika Hakkinen", driver2="David Coulthard")) 

# 		self.drivers = []

# 		self.drivers.append(test_driver_functions.gen_dummy_driver(model=self, name="Jacques Villeneuve"))
# 		self.drivers.append(test_driver_functions.gen_dummy_driver(model=self, name="Heinz-Harald Frentzen"))
# 		self.drivers.append(test_driver_functions.gen_dummy_driver(model=self, name="Michael Schumacher"))
# 		self.drivers.append(test_driver_functions.gen_dummy_driver(model=self, name="Eddie Irvine"))
# 		self.drivers.append(test_driver_functions.gen_dummy_driver(model=self, name="Mika Hakkinen"))
# 		self.drivers.append(test_driver_functions.gen_dummy_driver(model=self, name="David Coulthard"))

# 		super().__init__(None, None)

def test_create_standings_dataframe():

	teams = {
		"Williams": ["Jacques Villeneuve", "Heinz-Harald Frentzen"],
		"Ferrari": ["Michael Schumacher", "Eddie Irvine"],
		"McLaren": ["Mika Hakkinen", "David Coulthard"],
	}

	drivers_standings_df, constructors_standings_df = standings_manager.create_standings_dataframe(teams)

	assert drivers_standings_df.columns.tolist() == ["Driver", "Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs", "Starts"]

	expected = [
		["Jacques Villeneuve", "Williams", 0, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Williams", 0, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferrari", 0, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferrari", 0, 0, 0, 0, 0, 0],
		["Mika Hakkinen", "McLaren", 0, 0, 0, 0, 0, 0],
		["David Coulthard", "McLaren", 0, 0, 0, 0, 0, 0],
		]
	
	assert drivers_standings_df.values.tolist() == expected

	assert constructors_standings_df.columns.tolist() == ["Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs"]

	expected = [
			["Williams", 0, 0, 0, 0, 0],
			["Ferrari", 0, 0, 0, 0, 0],
			["McLaren", 0, 0, 0, 0, 0],
		]
	
	assert constructors_standings_df.values.tolist() == expected

def test_standings_manager_setup():
	model = create_model.create_model()
	standings_manager_instance = standings_manager.StandingsManager(model)

	expected = [
		["Jacques Villeneuve", "Williams", 0, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Williams", 0, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferrari", 0, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferrari", 0, 0, 0, 0, 0, 0],
		["Giancarlo Fisichella", "Benetton", 0, 0, 0, 0, 0, 0],
		["Alexander Wurz", "Benetton", 0, 0, 0, 0, 0, 0],
		["Mika Hakkinen", "McLaren", 0, 0, 0, 0, 0, 0],
		["David Coulthard", "McLaren", 0, 0, 0, 0, 0, 0],
		]

	assert standings_manager_instance.drivers_standings_df.head(8).values.tolist() == expected

	expected = [
			["Williams", 0, 0, 0, 0, 0],
			["Ferrari", 0, 0, 0, 0, 0],
			["Benetton", 0, 0, 0, 0, 0],
			["McLaren", 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.constructors_standings_df.head(4).values.tolist() == expected

def test_update_standings():
	model = create_model.create_model()
	standings_manager_instance = standings_manager.StandingsManager(model)

	columns = ["Driver"]
	data = ["Mika Hakkinen", "David Coulthard", "Eddie Irvine", "Michael Schumacher", "Jacques Villeneuve", "Heinz-Harald Frentzen", "Giancarlo Fisichella", "Alexander Wurz"]
	result1 = pd.DataFrame(columns=columns, data=data)

	standings_manager_instance.update_standings(result1)

	expected = [
		["Mika Hakkinen", "McLaren", 10, 0, 0, 0, 0, 0],
		["David Coulthard", "McLaren", 6, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferrari", 4, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferrari", 3, 0, 0, 0, 0, 0],
		["Jacques Villeneuve", "Williams", 2, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Williams", 1, 0, 0, 0, 0, 0],
		# ["Giancarlo Fisichella", "Benetton", 0, 0, 0, 0, 0, 0],
		# ["Alexander Wurz", "Benetton", 0, 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.drivers_standings_df.head(6).values.tolist() == expected

	data = ["Michael Schumacher", "Eddie Irvine", "Mika Hakkinen", "Jacques Villeneuve", "David Coulthard", "Heinz-Harald Frentzen", "Giancarlo Fisichella", "Alexander Wurz"]
	result2 = pd.DataFrame(columns=columns, data=data)

	standings_manager_instance.update_standings(result2)

	expected = [
		["Mika Hakkinen", "McLaren", 14, 0, 0, 0, 0, 0],
		["Michael Schumacher", "Ferrari", 13, 0, 0, 0, 0, 0],
		["Eddie Irvine", "Ferrari", 10, 0, 0, 0, 0, 0],
		["David Coulthard", "McLaren", 8, 0, 0, 0, 0, 0],
		["Jacques Villeneuve", "Williams", 5, 0, 0, 0, 0, 0],
		["Heinz-Harald Frentzen", "Williams", 2, 0, 0, 0, 0, 0],
		# ["Giancarlo Fisichella", "Benetton", 0, 0, 0, 0, 0, 0],
		# ["Alexander Wurz", "Benetton", 0, 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.drivers_standings_df.head(6).values.tolist() == expected

	expected = [
			["Ferrari", 23, 0, 0, 0, 0],
			["McLaren", 22, 0, 0, 0, 0],
			["Williams", 7, 0, 0, 0, 0],
			# ["Arrows", 0, 0, 0, 0, 0],
			# ["Benetton", 0, 0, 0, 0, 0],
		]
	
	assert standings_manager_instance.constructors_standings_df.head(3).values.tolist() == expected

	#TODO test stats such as starts, DNFs in standings df

