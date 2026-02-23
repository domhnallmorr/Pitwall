import { describe, it, expect, beforeEach, vi } from 'vitest';

const { apiMock } = vi.hoisted(() => {
	const mock = {
		startCareer: vi.fn(),
		loadGame: vi.fn(),
		checkSave: vi.fn(),
		getGrid: vi.fn(),
		getCalendar: vi.fn(),
		getStandings: vi.fn(),
		advanceWeek: vi.fn(),
		skipEvent: vi.fn(),
		simulateRace: vi.fn(),
		getEmails: vi.fn(),
		getStaff: vi.fn(),
		getDriver: vi.fn(),
		getCar: vi.fn(),
		getFinance: vi.fn(),
		getFacilities: vi.fn(),
		ping: vi.fn(),
		loadRoster: vi.fn(),
		onData: vi.fn(),
	};
	return { apiMock: mock };
});

vi.mock('./api.js', () => ({ default: apiMock }));
vi.mock('./views/navigation.js', () => ({ default: class { showView() {} } }));
vi.mock('./views/grid.js', () => ({
	default: class {
		constructor() { this.baseYear = 1998; }
		setYearRequestHandler() {}
		setDriverSelectHandler() {}
		setDriverCountryMap() {}
		setSeasonBase() {}
		getActiveYear() { return 1998; }
		render() {}
	},
}));
vi.mock('./views/standings.js', () => ({ default: class { setDriverSelectHandler() {} render() {} } }));
vi.mock('./views/calendar.js', () => ({ default: class { render() {} } }));
vi.mock('./views/email.js', () => ({ default: class { render() {} updateUnreadBadge() {} } }));
vi.mock('./views/staff.js', () => ({ default: class { render() {} } }));
vi.mock('./views/driver.js', () => ({ default: class { constructor() { this.currentDriverName = null; } render() {} } }));
vi.mock('./views/car.js', () => ({ default: class { render() {} } }));
vi.mock('./views/finance.js', () => ({ default: class { render() {} } }));
vi.mock('./views/facilities.js', () => ({ default: class { render() {} } }));

describe('renderer smoke', () => {
	beforeEach(() => {
		vi.resetModules();
		vi.clearAllMocks();
		document.body.innerHTML = `
			<div id="title-screen"></div>
			<div id="game-dashboard" style="display:none;"></div>
			<div id="title-start-actions"></div>
			<button id="start-career-btn"></button>
			<button id="load-game-btn" disabled></button>
			<div id="team-select-screen" style="display:none;"></div>
			<div id="team-select-buttons"></div>
			<div id="team-name"></div>
			<div id="current-week"></div>
			<div id="next-event"></div>
			<div id="team-balance"></div>
			<button id="ping-btn"></button>
			<button id="roster-btn"></button>
			<button id="advance-btn"></button>
			<div id="test-session-modal" style="display:none;"></div>
			<button id="test-no-btn"></button>
			<button id="simulate-race-btn"></button>
			<button id="return-dashboard-btn"></button>
			<div id="race-view" style="display:none;"></div>
			<div id="race-event-name"></div>
			<div id="race-week-display"></div>
			<div id="race-results-container" style="display:none;"></div>
			<table><tbody id="race-results-body"></tbody></table>
			<div id="grid-view" style="display:none;"></div>
			<div id="staff-view" style="display:none;"></div>
			<div id="standings-view" style="display:none;"></div>
			<div id="finance-view" style="display:none;"></div>
			<div id="car-view" style="display:none;"></div>
		`;
	});

	it('initializes and wires basic controls', async () => {
		let ipcHandler = null;
		apiMock.onData.mockImplementation((cb) => { ipcHandler = cb; });

		await import('./renderer.js');

		expect(apiMock.checkSave).toHaveBeenCalledTimes(1);

		document.getElementById('start-career-btn').click();
		expect(document.getElementById('team-select-screen').style.display).toBe('block');
		const teamButtons = document.querySelectorAll('.team-select-btn');
		expect(teamButtons.length).toBeGreaterThan(0);
		teamButtons[0].click();
		expect(apiMock.startCareer).toHaveBeenCalledTimes(1);
		expect(apiMock.startCareer.mock.calls[0][0]).toBe('Warrick');

		ipcHandler(JSON.stringify({ type: 'save_status', data: { has_save: true } }));
		expect(document.getElementById('load-game-btn').disabled).toBe(false);
	});
});
