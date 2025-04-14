class CarModel:
	def __init__(self, speed: int):
		self.speed = speed

	def update_speed(self, speed: int) -> None:
		assert speed > 0 and speed <= 100, f"Invalid speed: {speed}"
		self.speed = speed

	def implement_car_development(self, speed_increase: int) -> None:
		self.speed += speed_increase
		
	def implement_testing_progess(self, speed_increase: int) -> None:
		self.speed += speed_increase