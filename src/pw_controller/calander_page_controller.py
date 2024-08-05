


class CalendarPageController:
	def __init__(self, controller):
		self.controller = controller

	@property	
	def model(self):
		return self.controller.model

	@property	
	def view(self):
		return self.controller.view

	def update_track_frame(self, idx):

		calendar_row = self.model.calendar.iloc[idx]

		track_model = self.model.get_track_model(calendar_row["Track"])
		
		data = {
			"title": track_model.title,
			"track": track_model.name,
		}

		self.view.calendar_page.update_track_frame(data)