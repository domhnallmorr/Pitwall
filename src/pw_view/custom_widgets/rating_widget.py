import flet as ft

class RatingWidget(ft.Row):
	def __init__(self, text):
        
		self.text_widget = ft.Text(text)
		self.update_row(50)

		super(RatingWidget, self).__init__(controls=self.controls)

	def attribute_to_stars(self, attribute):
		"""
		Converts a 0-100 attribute value into a 1-5 star rating.
		
		Args:
			attribute (int): The attribute value (0-100).
		
		Returns:
			int: Star rating (1-5).
		"""
		# Clamp the attribute between 0 and 100
		attribute = max(0, min(100, attribute))
		# Map the attribute to a 1-5 scale
		return max(1, min(5, (attribute // 20) + 1))

	def create_star_row(self, star_rating):
		# Create a row of star icons based on the star_rating
		stars = [
			ft.Icon(ft.icons.SQUARE if i < star_rating else ft.icons.SQUARE_OUTLINED, color=ft.colors.PRIMARY)
			for i in range(5)
		]
		
		self.icon_row = ft.Row(controls=stars, spacing=1)

		self.controls = [
			self.text_widget,
			self.icon_row
		]

	def update_row(self, rating):
		star_rating = self.attribute_to_stars(rating)
		self.create_star_row(star_rating)

