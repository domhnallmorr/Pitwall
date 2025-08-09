from __future__ import annotations
from typing import TYPE_CHECKING

from pw_model.track.track_model import TrackModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	
def load_tracks(model: Model, track_files: list[str]) -> list[TrackModel]:
	tracks = []

	for file in track_files:
		with open(file) as f:
			data = f.readlines()

		data = [l.rstrip() for l in data]
		track = TrackModel(model, data)
		tracks.append(track)

	return tracks