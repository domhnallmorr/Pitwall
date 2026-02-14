/**
 * API Module
 * Wrapper for Electron IPC calls.
 */

const API = {
	startCareer: () => window.electronAPI.sendToPython({ type: 'start_career' }),
	getGrid: () => window.electronAPI.sendToPython({ type: 'get_grid' }),
	getCalendar: () => window.electronAPI.sendToPython({ type: 'get_calendar' }),
	getStandings: () => window.electronAPI.sendToPython({ type: 'get_standings' }),
	advanceWeek: () => window.electronAPI.sendToPython({ type: 'advance_week' }),
	skipEvent: () => window.electronAPI.sendToPython({ type: 'skip_event' }),
	simulateRace: () => window.electronAPI.sendToPython({ type: 'simulate_race' }),
	getEmails: () => window.electronAPI.sendToPython({ type: 'get_emails' }),
	readEmail: (emailId) => window.electronAPI.sendToPython({ type: 'read_email', email_id: emailId }),
	getStaff: () => window.electronAPI.sendToPython({ type: 'get_staff' }),
	getFinance: () => window.electronAPI.sendToPython({ type: 'get_finance' }),
	getFacilities: () => window.electronAPI.sendToPython({ type: 'get_facilities' }),
	ping: () => window.electronAPI.sendToPython({ type: 'ping' }),
	loadRoster: () => window.electronAPI.sendToPython({ type: 'load_roster' }),

	// Listener for incoming data
	onData: (callback) => window.electronAPI.onPythonData(callback)
};

export default API;
