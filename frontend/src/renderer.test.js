import { describe, it, expect, beforeEach, vi } from 'vitest';

const { apiMock, facilitiesFns, viewFns } = vi.hoisted(() => {
	const mock = {
		startCareer: vi.fn(),
		loadGame: vi.fn(),
		checkSave: vi.fn(),
		getGrid: vi.fn(),
		getCalendar: vi.fn(),
		getStandings: vi.fn(),
		advanceWeek: vi.fn(),
		skipEvent: vi.fn(),
		attendTest: vi.fn(),
		simulateRace: vi.fn(),
		getEmails: vi.fn(),
		getStaff: vi.fn(),
		updateWorkforce: vi.fn(),
		getReplacementCandidates: vi.fn(),
		getManagerReplacementCandidates: vi.fn(),
		getTechnicalDirectorReplacementCandidates: vi.fn(),
		replaceDriver: vi.fn(),
		replaceCommercialManager: vi.fn(),
		replaceTechnicalDirector: vi.fn(),
		getDriver: vi.fn(),
		getCar: vi.fn(),
		startCarDevelopment: vi.fn(),
		repairCarWear: vi.fn(),
		getFinance: vi.fn(),
		getFacilities: vi.fn(),
		previewFacilitiesUpgrade: vi.fn(),
		startFacilitiesUpgrade: vi.fn(),
		ping: vi.fn(),
		loadRoster: vi.fn(),
		onData: vi.fn(),
	};
	return {
		apiMock: mock,
		facilitiesFns: {
			renderPreview: vi.fn(),
			closeUpgradeModal: vi.fn(),
		},
		viewFns: {
			gridRender: vi.fn(),
			standingsRender: vi.fn(),
			calendarRender: vi.fn(),
			emailRender: vi.fn(),
			emailUnread: vi.fn(),
			staffRender: vi.fn(),
			driverMarketRender: vi.fn(),
			driverRender: vi.fn(),
			carRender: vi.fn(),
			financeRender: vi.fn(),
			facilitiesRender: vi.fn(),
		},
	};
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
		render(...args) { viewFns.gridRender(...args); }
	},
}));
vi.mock('./views/standings.js', () => ({ default: class { setDriverSelectHandler() {} render(...args) { viewFns.standingsRender(...args); } } }));
vi.mock('./views/calendar.js', () => ({ default: class { render(...args) { viewFns.calendarRender(...args); } } }));
vi.mock('./views/email.js', () => ({ default: class { render(...args) { viewFns.emailRender(...args); } updateUnreadBadge(...args) { viewFns.emailUnread(...args); } } }));
vi.mock('./views/staff.js', () => ({ default: class { setReplaceDriverHandler() {} setReplaceCommercialManagerHandler() {} setReplaceTechnicalDirectorHandler() {} setUpdateWorkforceHandler() {} render(...args) { viewFns.staffRender(...args); } } }));
vi.mock('./views/driver.js', () => ({ default: class { constructor() { this.currentDriverName = null; } render(...args) { viewFns.driverRender(...args); } } }));
vi.mock('./views/driver_market.js', () => ({ default: class { setBackHandler() {} setSignHandler() {} render(...args) { viewFns.driverMarketRender(...args); } } }));
vi.mock('./views/car.js', () => ({ default: class { setStartDevelopmentHandler() {} setRepairWearHandler() {} render(...args) { viewFns.carRender(...args); } } }));
vi.mock('./views/finance.js', () => ({ default: class { render(...args) { viewFns.financeRender(...args); } } }));
vi.mock('./views/facilities.js', () => ({
	default: class {
		setPreviewHandler() {}
		setStartUpgradeHandler() {}
		closeUpgradeModal() { facilitiesFns.closeUpgradeModal(); }
		renderPreview(...args) { facilitiesFns.renderPreview(...args); }
		render(...args) { viewFns.facilitiesRender(...args); }
	},
}));

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
			<div id="test-km-modal" style="display:none;"></div>
			<button id="test-no-btn"></button>
			<button id="test-yes-btn"></button>
			<input id="test-km-input" value="500" />
			<div id="test-km-value"></div>
			<div id="test-km-cost"></div>
			<button id="test-km-cancel-btn"></button>
			<button id="test-km-confirm-btn"></button>
			<button id="simulate-race-btn"></button>
			<button id="return-dashboard-btn"></button>
			<div id="race-view" style="display:none;"></div>
			<div id="race-event-name"></div>
			<div id="race-week-display"></div>
			<div id="race-lap-counter"></div>
			<div id="race-leader-display"></div>
			<div id="race-fastest-lap-display"></div>
			<div id="race-latest-commentary"></div>
			<div id="race-commentary-log"></div>
			<button id="race-tab-timing" class="race-tab-btn active" data-race-tab="timing"></button>
			<button id="race-tab-commentary" class="race-tab-btn" data-race-tab="commentary"></button>
			<button id="race-tab-chart" class="race-tab-btn" data-race-tab="chart"></button>
			<button id="race-tab-laptimes" class="race-tab-btn" data-race-tab="laptimes"></button>
			<div id="race-panel-timing"></div>
			<div id="race-panel-commentary" style="display:none;"></div>
			<div id="race-panel-chart" style="display:none;"></div>
			<div id="race-panel-laptimes" style="display:none;"></div>
			<div id="race-lap-chart-legend"></div>
			<svg id="race-lap-chart-svg"></svg>
			<select id="race-laptime-driver-1"></select>
			<select id="race-laptime-driver-2"></select>
			<select id="race-laptime-driver-3"></select>
			<select id="race-laptime-driver-4"></select>
			<div id="race-laptime-legend"></div>
			<svg id="race-laptime-svg"></svg>
			<button id="race-pause-btn"></button>
			<button id="race-prev-lap-btn"></button>
			<button id="race-next-lap-btn"></button>
			<div id="race-results-container" style="display:none;"></div>
			<table><tbody id="race-results-body"></tbody></table>
			<div id="home-view" style="display:none;"></div>
			<div id="email-view" style="display:none;"></div>
			<div id="calendar-view" style="display:none;"></div>
			<div id="grid-view" style="display:none;"></div>
			<div id="staff-view" style="display:none;"></div>
			<div id="standings-view" style="display:none;"></div>
			<div id="finance-view" style="display:none;"></div>
			<div id="facilities-view" style="display:none;"></div>
			<div id="driver-view" style="display:none;"></div>
			<div id="driver-market-view" style="display:none;"></div>
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

	it('refreshes staff/finance/car/emails on successful workforce update', async () => {
		let ipcHandler = null;
		apiMock.onData.mockImplementation((cb) => { ipcHandler = cb; });

		await import('./renderer.js');

		ipcHandler(JSON.stringify({ type: 'workforce_updated', status: 'success', data: {} }));

		expect(apiMock.getStaff).toHaveBeenCalledTimes(1);
		expect(apiMock.getFinance).toHaveBeenCalledTimes(1);
		expect(apiMock.getCar).toHaveBeenCalledTimes(1);
		expect(apiMock.getEmails).toHaveBeenCalledTimes(1);
	});

	it('does not refresh views on workforce update error', async () => {
		let ipcHandler = null;
		apiMock.onData.mockImplementation((cb) => { ipcHandler = cb; });

		await import('./renderer.js');

		ipcHandler(JSON.stringify({ type: 'workforce_updated', status: 'error', message: 'bad input' }));

		expect(apiMock.getStaff).not.toHaveBeenCalled();
		expect(apiMock.getFinance).not.toHaveBeenCalled();
		expect(apiMock.getCar).not.toHaveBeenCalled();
	});

	it('handles key IPC update branches end-to-end', async () => {
		vi.useFakeTimers();
		let ipcHandler = null;
		apiMock.onData.mockImplementation((cb) => { ipcHandler = cb; });

		await import('./renderer.js');

		ipcHandler(JSON.stringify({
			type: 'game_started',
			status: 'success',
			data: {
				team_name: 'Warrick',
				week_display: 'Week 1 1998',
				next_event_display: 'Next: Albert Park - Week 10',
				year: 1998,
				balance: 1000000,
				unread_count: 2,
			},
		}));
		expect(apiMock.getStandings).toHaveBeenCalled();
		expect(apiMock.getGrid).toHaveBeenCalledWith(1998);
		expect(apiMock.getGrid).toHaveBeenCalledWith(1999);

		document.getElementById('finance-view').style.display = 'block';
		ipcHandler(JSON.stringify({
			type: 'week_advanced',
			status: 'success',
			data: {
				new_date_display: 'Week 2 1998',
				next_event_display: 'Next: Test - Week 5',
				button_text: 'ADVANCE',
				event_active: false,
				year: 1998,
				balance: 900000,
			},
		}));
		expect(apiMock.getEmails).toHaveBeenCalled();
		expect(apiMock.getFinance).toHaveBeenCalled();

		ipcHandler(JSON.stringify({
			type: 'race_result',
			status: 'success',
			data: {
				total_laps: 2,
				lap_history: [
					{
						lap: 1,
						order: [
							{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83000, best_lap_ms: 83000, gap_display: 'LEADER', status: 'RUNNING' },
							{ driver_id: 2, position: 2, driver_name: 'B', team_name: 'T2', last_lap_ms: 83500, best_lap_ms: 83500, gap_display: '+0.500s', status: 'RUNNING' },
							{ driver_id: 3, position: 3, driver_name: 'C', team_name: 'T3', last_lap_ms: 84000, best_lap_ms: 84000, gap_display: '+1.000s', status: 'RUNNING' },
						],
						events: [{ type: 'fastest_lap', lap: 1, driver_name: 'A', lap_time_ms: 83000 }],
					},
					{
						lap: 2,
						order: [
							{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83200, best_lap_ms: 83000, gap_display: 'LEADER', status: 'FINISHED' },
							{ driver_id: 2, position: 2, driver_name: 'B', team_name: 'T2', last_lap_ms: 84000, best_lap_ms: 83500, gap_display: '+1 Lap', status: 'FINISHED' },
							{ driver_id: 3, position: 3, driver_name: 'C', team_name: 'T3', last_lap_ms: null, best_lap_ms: 84000, gap_display: '+1 Lap', status: 'DNF' },
						],
						events: [
							{ type: 'pit_stop', lap: 2, driver_id: 2, driver_name: 'B', stop_number: 1, fuel_added_kg: 20.0 },
							{ type: 'position_change', lap: 2, driver_name: 'B', to_position: 2 },
						],
					},
				],
				results: [
					{ position: 1, driver_name: 'A', team_name: 'T1', points: 10 },
					{ status: 'DNF', crash_out: true, mechanical_out: false, driver_name: 'B', team_name: 'T2', points: 0 },
					{ status: 'DNF', crash_out: false, mechanical_out: true, driver_name: 'C', team_name: 'T3', points: 0 },
				],
			},
		}));
		await vi.advanceTimersByTimeAsync(950);
		expect(document.getElementById('race-results-body').children.length).toBe(3);
		expect(document.getElementById('race-lap-counter').textContent).toBe('2 / 2');
		expect(document.getElementById('race-leader-display').textContent).toContain('A');
		expect(document.getElementById('race-fastest-lap-display').textContent).toContain('A');
		expect(document.getElementById('race-latest-commentary').textContent).toContain('Lap 2');
		expect(document.getElementById('race-latest-commentary').textContent).toContain('moves up to P2');
		expect(document.getElementById('race-commentary-log').textContent).toContain('fastest lap');
		expect(document.getElementById('race-commentary-log').textContent).toContain('pits for fuel');
		expect(document.getElementById('race-results-body').children[1].children[3].textContent).toBe('1');
		expect(document.querySelectorAll('#race-lap-chart-svg .race-lap-chart-line').length).toBe(3);
		expect(document.getElementById('race-lap-chart-legend').children.length).toBe(3);
		expect(document.querySelectorAll('#race-laptime-svg .race-lap-chart-line').length).toBe(3);
		expect(document.getElementById('race-laptime-legend').children.length).toBe(3);
		expect(document.querySelectorAll('#race-laptime-svg .race-laptime-pit-marker').length).toBe(1);
		expect(document.getElementById('race-laptime-legend').textContent).toContain('square = pit lap');
		expect(document.getElementById('race-laptime-driver-1').value).toBe('1');
		document.getElementById('race-tab-chart').click();
		expect(document.getElementById('race-panel-chart').style.display).toBe('');
		expect(document.getElementById('race-panel-timing').style.display).toBe('none');
		document.getElementById('race-tab-commentary').click();
		expect(document.getElementById('race-panel-commentary').style.display).toBe('');
		expect(document.getElementById('race-panel-chart').style.display).toBe('none');
		document.getElementById('race-tab-laptimes').click();
		expect(document.getElementById('race-panel-laptimes').style.display).toBe('');
		expect(document.getElementById('race-panel-commentary').style.display).toBe('none');
		expect(apiMock.getFinance).toHaveBeenCalled();

		ipcHandler(JSON.stringify({ type: 'car_development_started', status: 'success' }));
		ipcHandler(JSON.stringify({ type: 'car_wear_repaired', status: 'success' }));
		expect(apiMock.getCar).toHaveBeenCalled();

		ipcHandler(JSON.stringify({ type: 'facilities_upgrade_started', status: 'success' }));
		expect(facilitiesFns.closeUpgradeModal).toHaveBeenCalled();
		expect(apiMock.getFacilities).toHaveBeenCalled();
		expect(apiMock.getEmails).toHaveBeenCalled();

		ipcHandler(JSON.stringify({
			type: 'facilities_upgrade_started',
			status: 'error',
			message: 'Unable to start',
		}));
		expect(facilitiesFns.renderPreview).toHaveBeenCalled();
		vi.useRealTimers();
	});

	it('pauses and resumes race autoplay', async () => {
		vi.useFakeTimers();
		let ipcHandler = null;
		apiMock.onData.mockImplementation((cb) => { ipcHandler = cb; });

		await import('./renderer.js');

		ipcHandler(JSON.stringify({
			type: 'race_result',
			status: 'success',
			data: {
				total_laps: 3,
				lap_history: [
					{
						lap: 1,
						order: [{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83000, best_lap_ms: 83000, gap_display: 'LEADER', status: 'RUNNING' }],
						events: [],
					},
					{
						lap: 2,
						order: [{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83100, best_lap_ms: 83000, gap_display: 'LEADER', status: 'RUNNING' }],
						events: [],
					},
					{
						lap: 3,
						order: [{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83200, best_lap_ms: 83000, gap_display: 'LEADER', status: 'FINISHED' }],
						events: [],
					},
				],
				results: [{ position: 1, driver_name: 'A', team_name: 'T1', points: 10 }],
			},
		}));

		expect(document.getElementById('race-lap-counter').textContent).toBe('1 / 3');
		document.getElementById('race-pause-btn').click();
		expect(document.getElementById('race-pause-btn').textContent).toBe('Resume');
		await vi.advanceTimersByTimeAsync(1000);
		expect(document.getElementById('race-lap-counter').textContent).toBe('1 / 3');
		document.getElementById('race-pause-btn').click();
		expect(document.getElementById('race-pause-btn').textContent).toBe('Pause');
		await vi.advanceTimersByTimeAsync(1000);
		expect(document.getElementById('race-lap-counter').textContent).toBe('3 / 3');
		vi.useRealTimers();
	});

	it('runs test/race control interactions and debug/load buttons', async () => {
		await import('./renderer.js');

		document.getElementById('load-game-btn').disabled = false;
		document.getElementById('load-game-btn').click();
		expect(apiMock.loadGame).toHaveBeenCalledTimes(1);
		document.getElementById('ping-btn').click();
		document.getElementById('roster-btn').click();
		expect(apiMock.ping).toHaveBeenCalledTimes(1);
		expect(apiMock.loadRoster).toHaveBeenCalledTimes(1);

		const advanceBtn = document.getElementById('advance-btn');
		const testModal = document.getElementById('test-session-modal');
		const testKmModal = document.getElementById('test-km-modal');
		const testKmInput = document.getElementById('test-km-input');
		const testKmValue = document.getElementById('test-km-value');
		const testKmCost = document.getElementById('test-km-cost');

		advanceBtn.textContent = 'GO TO TEST';
		advanceBtn.click();
		expect(testModal.style.display).toBe('flex');

		document.getElementById('test-no-btn').click();
		expect(testModal.style.display).toBe('none');
		expect(apiMock.skipEvent).toHaveBeenCalledTimes(1);

		advanceBtn.click();
		document.getElementById('test-yes-btn').click();
		expect(testModal.style.display).toBe('none');
		expect(testKmModal.style.display).toBe('flex');
		expect(testKmValue.textContent).toBe('500');
		expect(testKmCost.textContent).toBe('$700,000');

		testKmInput.value = '900';
		testKmInput.dispatchEvent(new window.Event('input'));
		expect(testKmValue.textContent).toBe('900');
		expect(testKmCost.textContent).toBe('$1,260,000');

		document.getElementById('test-km-cancel-btn').click();
		expect(testKmModal.style.display).toBe('none');
		expect(testModal.style.display).toBe('flex');

		document.getElementById('test-yes-btn').click();
		document.getElementById('test-km-confirm-btn').click();
		expect(apiMock.attendTest).toHaveBeenCalledWith(900);

		document.getElementById('next-event').textContent = 'Next: Monaco Grand Prix - Week 6';
		document.getElementById('current-week').textContent = 'Week 6 1998';
		document.getElementById('race-results-container').style.display = 'block';
		const simulateBtn = document.getElementById('simulate-race-btn');
		simulateBtn.disabled = true;
		simulateBtn.textContent = 'OLD';
		simulateBtn.style.display = 'none';

		advanceBtn.textContent = 'GO TO RACE';
		advanceBtn.click();
		expect(document.getElementById('race-view').style.display).toBe('flex');
		expect(document.getElementById('race-event-name').textContent).toBe('Monaco Grand Prix');
		expect(document.getElementById('race-week-display').textContent).toBe('Week 6 1998');
		expect(simulateBtn.disabled).toBe(false);
		expect(simulateBtn.textContent).toBe('SIMULATE RACE');
		expect(simulateBtn.style.display).toBe('');
		expect(document.getElementById('race-results-container').style.display).toBe('none');
		expect(document.getElementById('race-commentary-log').textContent).toBe('');
		expect(document.getElementById('race-lap-counter').textContent).toBe('0 / 0');
		expect(document.getElementById('race-latest-commentary').textContent).toBe('Awaiting lights out.');

		simulateBtn.click();
		expect(apiMock.simulateRace).toHaveBeenCalledTimes(1);
		expect(simulateBtn.disabled).toBe(true);
		expect(simulateBtn.textContent).toBe('SIMULATING...');

		advanceBtn.classList.add('event-active');
		document.getElementById('return-dashboard-btn').click();
		expect(document.getElementById('race-view').style.display).toBe('none');
		expect(advanceBtn.textContent).toBe('ADVANCE');
		expect(advanceBtn.classList.contains('event-active')).toBe(false);
	});

	it('handles remaining ipc fan-out branches and malformed payload', async () => {
		let ipcHandler = null;
		apiMock.onData.mockImplementation((cb) => { ipcHandler = cb; });

		await import('./renderer.js');

		ipcHandler(JSON.stringify({ type: 'game_loaded', status: 'success', data: { team_name: 'Warrick', week_display: 'Week 1 1998', next_event_display: 'Next: A - Week 2', year: 1998, balance: 1, unread_count: 0 } }));
		ipcHandler(JSON.stringify({ type: 'grid_data', data: { rows: [] }, year: 1998 }));
		ipcHandler(JSON.stringify({ type: 'standings_data', data: { drivers: [], constructors: [] } }));
		ipcHandler(JSON.stringify({ type: 'calendar_data', data: [] }));
		ipcHandler(JSON.stringify({ type: 'email_data', data: { emails: [], unread_count: 0 } }));
		ipcHandler(JSON.stringify({ type: 'email_read', data: { unread_count: 1 } }));
		ipcHandler(JSON.stringify({ type: 'staff_data', data: { drivers: [] } }));
		ipcHandler(JSON.stringify({ type: 'replacement_candidates', data: { candidates: [] } }));
		ipcHandler(JSON.stringify({ type: 'driver_replaced', status: 'success' }));
		ipcHandler(JSON.stringify({ type: 'driver_data', data: { name: 'Driver X' } }));
		ipcHandler(JSON.stringify({ type: 'car_data', data: { teams: [] } }));
		ipcHandler(JSON.stringify({ type: 'finance_data', data: { summary: {} } }));
		ipcHandler(JSON.stringify({ type: 'facilities_data', data: { teams: [] } }));
		ipcHandler(JSON.stringify({ type: 'facilities_upgrade_preview', data: { projected_facilities: 90 }, status: 'success' }));
		ipcHandler(JSON.stringify({ type: 'status', message: 'ok' }));
		ipcHandler('not-json');

		expect(viewFns.gridRender).toHaveBeenCalled();
		expect(viewFns.standingsRender).toHaveBeenCalled();
		expect(viewFns.calendarRender).toHaveBeenCalled();
		expect(viewFns.emailRender).toHaveBeenCalled();
		expect(viewFns.emailUnread).toHaveBeenCalled();
		expect(viewFns.staffRender).toHaveBeenCalled();
		expect(viewFns.driverMarketRender).toHaveBeenCalled();
		expect(viewFns.driverRender).toHaveBeenCalled();
		expect(viewFns.carRender).toHaveBeenCalled();
		expect(viewFns.financeRender).toHaveBeenCalled();
		expect(viewFns.facilitiesRender).toHaveBeenCalled();
		expect(facilitiesFns.renderPreview).toHaveBeenCalled();
		expect(apiMock.getGrid).toHaveBeenCalled();
	});
});
