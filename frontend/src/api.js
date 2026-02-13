/**
 * API Module
 * Wrapper for Electron IPC calls.
 */

const API = {
	startCareer: () => window.electronAPI.sendToPython({ type: 'start_career' }),
	getGrid: () => window.electronAPI.sendToPython({ type: 'get_grid' }),
	getCalendar: () => window.electronAPI.sendToPython({ type: 'get_calendar' }),
	getStandings: () => window.electronAPI.sendToPython({ type: 'get_standings' }),
	ping: () => window.electronAPI.sendToPython({ type: 'ping' }),
	loadRoster: () => window.electronAPI.sendToPython({ type: 'load_roster' }),

	// Listener for incoming data
	onData: (callback) => window.electronAPI.onPythonData(callback)
};

export default API;
