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
	simulateRace: () => window.electronAPI.sendToPython({ type: 'simulate_race' }),
	getEmails: () => window.electronAPI.sendToPython({ type: 'get_emails' }),
	readEmail: (emailId) => window.electronAPI.sendToPython({ type: 'read_email', email_id: emailId }),
	getStaff: () => window.electronAPI.sendToPython({ type: 'get_staff' }),
	getReplacementCandidates: (driverId) => window.electronAPI.sendToPython({ type: 'get_replacement_candidates', driver_id: driverId }),
	replaceDriver: (driverId, incomingDriverId) => window.electronAPI.sendToPython({
		type: 'replace_driver',
		driver_id: driverId,
		incoming_driver_id: incomingDriverId
	}),
	getDriver: (name) => window.electronAPI.sendToPython({ type: 'get_driver', name }),
	getCar: () => window.electronAPI.sendToPython({ type: 'get_car' }),
	startCarDevelopment: (developmentType) => window.electronAPI.sendToPython({ type: 'start_car_development', development_type: developmentType }),
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
