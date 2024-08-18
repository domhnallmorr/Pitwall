
from pw_model import load_roster
from pw_model.season import season_model
from pw_model.email import email_model

class Model:
	def __init__(self, roster, run_directory):
		self.run_directory = run_directory

		self.tracks = []
		if roster is not None:
			load_roster.load_roster(self, roster)

		self.year = 1998
		self.season = season_model.SeasonModel(self)

		self.inbox = email_model.Inbox(self)

	def get_driver_model(self, driver_name):
		driver_model = None

		for d in self.drivers:
			if d.name == driver_name:
				driver_model = d
				break
			
		return driver_model
	
	def get_team_model(self, team_name):
		driver_model = None

		for t in self.teams:
			if t.name == team_name:
				team_model = t
				break
			
		return team_model
	
	def get_track_model(self, track_name):
		track_model = None

		for track in self.tracks:
			if track.name == track_name:
				track_model = track

		assert track_model is not None, f"Failed to Find Track {track_name}"

		return track_model
	
	def advance(self):
		self.season.advance_one_week()

	def end_season(self):
		self.season.setup_new_season_variables()

		for driver in self.drivers:
			driver.end_season()

		for team in self.teams:
			team.end_season()

		self.year += 1
		