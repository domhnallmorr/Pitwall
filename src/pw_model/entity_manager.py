from __future__ import annotations
from typing import TYPE_CHECKING, Union
import logging

from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.driver.driver_model import DriverModel
	from pw_model.senior_staff.commercial_manager import CommercialManager
	from pw_model.engine.engine_supplier_model import EngineSupplierModel
	from pw_model.sponsors.sponsor_model import SponsorModel
	from pw_model.team.team_model import TeamModel
	from pw_model.senior_staff.team_principal import TeamPrincipalModel
	from pw_model.senior_staff.technical_director import TechnicalDirector
	from pw_model.track.track_model import TrackModel
	from pw_model.tyre.tyre_supplier_model import TyreSupplierModel



class EntityManager:
	"""
	Handles lookup of specific entity model instances based on identifiers.
	"""
	def __init__(self, model: Model):
		self._model = model # Keep a reference to the main model

	@property
	def no_of_active_team_principals(self) -> int:
		# active team principals are those who are not retiring or retired
		return len([tp for tp in self._model.team_principals if tp.retiring is False and tp.retired is False])

	def setup_new_season(self) -> None:
		self.add_new_drivers()
		self.add_new_managers()
		self.add_new_sponsors()

	def get_commercial_manager_model(self, name: str) -> CommercialManager:
		commercial_manager_model = None

		for c in self._model.commercial_managers:
			if c.name == name:
				commercial_manager_model = c
				break
			
		return commercial_manager_model
	
	def get_driver_model(self, driver_name: str) -> DriverModel:
		driver_model = None

		for d in self._model.drivers:
			if d.name == driver_name:
				driver_model = d
				break
			
		return driver_model

	def get_engine_supplier_model(self, name: str) -> EngineSupplierModel:
		engine_supplier_model = None

		for e in self._model.engine_suppliers:
			if e.name == name:
				engine_supplier_model = e
				break
			
		return engine_supplier_model
	
	def get_sponsor_model(self, name: str) -> SponsorModel:
		sponsor_model = None

		for s in self._model.sponsors:
			if s.name == name:
				sponsor_model = s
				break
			
		return sponsor_model

	def get_team_model(self, team_name: str) -> TeamModel:
		team_model = None

		for t in self._model.teams:
			if t.name == team_name:
				team_model = t
				break
			
		return team_model
	
	def get_team_principal_model(self, team_principal_name: str) -> Union[TeamPrincipalModel, None]:
		team_principal_model = None

		for tp in self._model.team_principals:
			if tp.name == team_principal_name:
				team_principal_model = tp
				break

		assert team_principal_model is not None, f"Team Principal {team_principal_name} not found"
		return team_principal_model
	
	def get_technical_director_model(self, name: str) -> TechnicalDirector:
		technical_director_model = None

		for t in self._model.technical_directors:
			if t.name == name:
				technical_director_model = t
				break
			
		return technical_director_model

	def get_track_model(self, track_name: str) -> TrackModel:
		track_model = None

		for track in self._model.tracks:
			if track.name == track_name:
				track_model = track

		assert track_model is not None, f"Failed to Find Track {track_name}"

		return track_model

	def get_tyre_supplier_model(self, name: str) -> TyreSupplierModel:
		tyre_supplier_model = None

		for t in self._model.tyre_suppliers:
			if t.name == name:
				tyre_supplier_model = t
				break
			
		return tyre_supplier_model

	def add_new_drivers(self) -> None:
		new_drivers: list[tuple[str, DriverModel]] = [d for d in self._model.future_drivers if int(d[0]) == self._model.year]

		for new_driver in new_drivers:
			new_driver[1].setup_season_stats()
			self._model.drivers.append(new_driver[1])
			self._model.future_drivers.remove(new_driver)
			logging.info(f"Added {new_driver[1].name} to drivers")

		# Check we don't have duplicate drivers
		drivers_names = [driver.name for driver in self._model.drivers]
		assert len(drivers_names) == len(set(drivers_names))
	
	def add_new_managers(self) -> None:
		new_managers = [m for m in self._model.future_managers if int(m[0]) == self._model.year]
		
		'''
		example of new_managers list
		[['1999', <pw_model.senior_staff.technical_director.TechnicalDirector object at 0x00000150339AA8A0>]]
		'''

		for new_manager in new_managers:
			if new_manager[1].role == StaffRoles.COMMERCIAL_MANAGER:
				self._model.commercial_managers.append(new_manager[1])
			elif new_manager[1].role == StaffRoles.TECHNICAL_DIRECTOR:
				self._model.technical_directors.append(new_manager[1])
			elif new_manager[1].role == StaffRoles.TEAM_PRINCIPAL:
				print("Adding new team principal")
				self._model.team_principals.append(new_manager[1])

			self._model.future_managers.remove(new_manager)
			logging.info(f"Added {new_manager[1].name} to managers")
			
	def add_new_sponsors(self) -> None:
		new_sponsors = [s for s in self._model.future_sponsors if int(s[0]) == self._model.year]
		
		for new_sponsor in new_sponsors:
			self._model.sponsors.append(new_sponsor[1])
			self._model.future_sponsors.remove(new_sponsor)
			logging.info(f"Added {new_sponsor[1].name} to sponsors")

		# Check we don't have duplicate sponsors
		sponsors_names = [sponsor.name for sponsor in self._model.sponsors]
		assert len(sponsors_names) == len(set(sponsors_names))