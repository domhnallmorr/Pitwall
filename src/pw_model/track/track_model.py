


class TrackModel:
	def __init__(self, model, data):
		self.model = model
		self.parse_data(data)

		'''
		Assume 155kg required to run race, round down a little for conservatism
		'''
		self.fuel_consumption = round((155/self.number_of_laps) - 0.1, 2)

		'''
		base tyre wear, 20 laps equates to 1 second loss in performance
		'''
		self.tyre_wear = int(1_000 / 20)

		self.pit_stop_loss = 20_000 #20s loss coming through pits

		self.dist_to_turn1 = 615 # distance from pole to turn 1 in meters
		
	def parse_data(self, data):
		self.name = None
		self.country = None
		self.location = None
		self.title = None
		self.number_of_laps = None
		self.base_laptime = None

		for line in data:
			if line.startswith("Name:"):
				self.name = line.split(":")[1].lstrip()
			if line.startswith("Country:"):
				self.country = line.split(":")[1].lstrip()
			if line.startswith("Location:"):
				self.location = line.split(":")[1].lstrip()
			if line.startswith("Title:"):
				self.title = line.split(":")[1].lstrip()
			if line.startswith("Laps:"):
				self.number_of_laps = int(line.split(":")[1].lstrip())
			if line.startswith("Base Laptime:"):
				self.base_laptime = int(line.split(":")[1].lstrip())


		assert self.name is not None
		assert self.country is not None
		assert self.location is not None
		assert self.title is not None
		assert self.number_of_laps is not None
		assert self.base_laptime is not None
	