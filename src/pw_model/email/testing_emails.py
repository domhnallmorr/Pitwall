from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.email.email_model import Inbox


def generate_testing_progress_email(inbox: Inbox) -> None:
	messages = [
		"Testing progress has yielded car speed improvements.",
		"Testing progress has resulted in car speed improvements.",
		"Testing progress has led to car speed improvements.",
	]
	return random.choice(messages)

def generate_testing_completed_email(inbox: Inbox, distance_km: int) -> None:
	messages = [
		f"Testing has been completed. We covered {distance_km} km.",
		f"The testing has been completed. We covered {distance_km} km.",
		f"Testing is now complete. We covered {distance_km} km.",
	]
	return random.choice(messages)