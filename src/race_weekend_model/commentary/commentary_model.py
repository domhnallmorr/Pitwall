import pandas as pd

from race_weekend_model.commentary.overtake_commentary import gen_overtake_message
from race_weekend_model.commentary.turn1_commentary import gen_leading_after_turn1_message

class CommentaryModel:
	def __init__(self) -> None:
		self.commentary_df = pd.DataFrame(columns=["Lap", "Message"])
		
	def add_message(self, lap: int, message: str) -> None:
		self.commentary_df.loc[len(self.commentary_df)] = [lap, message]

	def gen_overtake_message(self, lap: int, driver_a: str, driver_b: str) -> None:
		msg = gen_overtake_message(driver_a, driver_b)
		self.add_message(lap, msg)

	def gen_leading_after_turn1_message(self, driver: str) -> None:
		msg = gen_leading_after_turn1_message(driver)
		self.add_message(1, msg)