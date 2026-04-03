/**
 * API Module
 * Wrapper for Electron IPC calls.
 */

const API = {
	startCareer: (teamName) => window.electronAPI.sendToPython(
		teamName ? { type: 'start_career', team_name: teamName } : { type: 'start_career' }
	),
	loadGame: () => window.electronAPI.sendToPython({ type: 'load_game' }),
	checkSave: () => window.electronAPI.sendToPython({ type: 'check_save' }),
	getGrid: (year) => window.electronAPI.sendToPython(
		year !== undefined ? { type: 'get_grid', year } : { type: 'get_grid' }
	),
	getCalendar: () => window.electronAPI.sendToPython({ type: 'get_calendar' }),
	getStandings: () => window.electronAPI.sendToPython({ type: 'get_standings' }),
	advanceWeek: () => window.electronAPI.sendToPython({ type: 'advance_week' }),
	skipEvent: () => window.electronAPI.sendToPython({ type: 'skip_event' }),
	attendTest: (kms) => window.electronAPI.sendToPython({ type: 'attend_test', kms }),
	getRaceWeekend: () => window.electronAPI.sendToPython({ type: 'get_race_weekend' }),
	simulateQualifying: () => window.electronAPI.sendToPython({ type: 'simulate_qualifying' }),
	simulateRace: () => window.electronAPI.sendToPython({ type: 'simulate_race' }),
	getEmails: () => window.electronAPI.sendToPython({ type: 'get_emails' }),
	readEmail: (emailId) => window.electronAPI.sendToPython({ type: 'read_email', email_id: emailId }),
	getStaff: () => window.electronAPI.sendToPython({ type: 'get_staff' }),
	updateWorkforce: (workforce) => window.electronAPI.sendToPython({ type: 'update_workforce', workforce }),
	getReplacementCandidates: (driverId) => window.electronAPI.sendToPython({ type: 'get_replacement_candidates', driver_id: driverId }),
	getManagerReplacementCandidates: (managerId) => window.electronAPI.sendToPython({ type: 'get_manager_replacement_candidates', manager_id: managerId }),
	getTechnicalDirectorReplacementCandidates: (directorId) => window.electronAPI.sendToPython({ type: 'get_technical_director_replacement_candidates', director_id: directorId }),
	getTitleSponsorReplacementCandidates: (sponsorName) => window.electronAPI.sendToPython({ type: 'get_title_sponsor_replacement_candidates', sponsor_name: sponsorName }),
	getTyreSupplierReplacementCandidates: (supplierName) => window.electronAPI.sendToPython({ type: 'get_tyre_supplier_replacement_candidates', supplier_name: supplierName }),
	replaceDriver: (driverId, incomingDriverId) => window.electronAPI.sendToPython({
		type: 'replace_driver',
		driver_id: driverId,
		incoming_driver_id: incomingDriverId
	}),
	replaceCommercialManager: (managerId, incomingManagerId) => window.electronAPI.sendToPython({
		type: 'replace_commercial_manager',
		manager_id: managerId,
		incoming_manager_id: incomingManagerId
	}),
	replaceTechnicalDirector: (directorId, incomingDirectorId) => window.electronAPI.sendToPython({
		type: 'replace_technical_director',
		director_id: directorId,
		incoming_director_id: incomingDirectorId
	}),
	replaceTitleSponsor: (sponsorName, incomingSponsorId) => window.electronAPI.sendToPython({
		type: 'replace_title_sponsor',
		sponsor_name: sponsorName,
		incoming_sponsor_id: incomingSponsorId
	}),
	replaceTyreSupplier: (supplierName, incomingSupplierId) => window.electronAPI.sendToPython({
		type: 'replace_tyre_supplier',
		supplier_name: supplierName,
		incoming_supplier_id: incomingSupplierId
	}),
	getDriver: (name) => window.electronAPI.sendToPython({ type: 'get_driver', name }),
	getCar: () => window.electronAPI.sendToPython({ type: 'get_car' }),
	startCarDevelopment: (developmentType) => window.electronAPI.sendToPython({ type: 'start_car_development', development_type: developmentType }),
	repairCarWear: (wearPoints) => window.electronAPI.sendToPython({ type: 'repair_car_wear', wear_points: wearPoints }),
	getFinance: () => window.electronAPI.sendToPython({ type: 'get_finance' }),
	getFacilities: () => window.electronAPI.sendToPython({ type: 'get_facilities' }),
	previewFacilitiesUpgrade: (points, years) => window.electronAPI.sendToPython({ type: 'preview_facilities_upgrade', points, years }),
	startFacilitiesUpgrade: (points, years) => window.electronAPI.sendToPython({ type: 'start_facilities_upgrade', points, years }),
	ping: () => window.electronAPI.sendToPython({ type: 'ping' }),
	loadRoster: () => window.electronAPI.sendToPython({ type: 'load_roster' }),

	// Listener for incoming data
	onData: (callback) => window.electronAPI.onPythonData(callback)
};

export default API;
