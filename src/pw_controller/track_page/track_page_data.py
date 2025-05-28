from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.track.track_model import TrackModel


@dataclass(frozen=True)
class TrackData:
	name: str
	length: float
	laps: int
	overtaking_delta: int


def get_track_page_data(model: Model, track: str) -> TrackData:
	track_model: TrackModel = model.entity_manager.get_track_model(track)

	return TrackData(
		name = track_model.name,
		length = track_model.length,
		laps = track_model.number_of_laps,
		overtaking_delta=track_model.overtaking_delta
	)