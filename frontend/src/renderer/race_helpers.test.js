import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
	collectRaceStrategySelections,
	enterRaceView,
	exitRaceView,
	openRaceStrategyScreen,
	renderRaceResults,
	renderRaceStrategyScreen,
	renderRaceWeekend,
} from './race_helpers.js';

vi.mock('./race_charts.js', () => ({
	formatLapTime: (ms) => (!Number.isFinite(ms) || ms <= 0 ? '-' : (ms / 1000).toFixed(3) + 's'),
	renderLapChart: vi.fn(),
	renderLaptimeChart: vi.fn(),
}));

describe('race_helpers', () => {
	beforeEach(() => {
		vi.useFakeTimers();
		document.body.innerHTML = `
			<div id="race-view" style="display:none;"></div>
			<div id="race-event-name"></div>
			<div id="race-week-display"></div>
			<div id="race-weekend-panel"></div>
			<div id="race-strategy-panel" style="display:none;"></div>
			<div id="race-circuit-display"></div>
			<div id="race-location-display"></div>
			<div id="race-laps-display"></div>
			<div id="race-pole-display"></div>
			<div id="race-weekend-status"></div>
			<div id="race-status-chip"></div>
			<div id="race-strategy-event-display"></div>
			<div id="race-strategy-cards"></div>
			<table><tbody id="race-qualifying-body"></tbody></table>
			<button id="simulate-qualifying-btn"></button>
			<button id="simulate-race-btn" style="display:none;"></button>
			<button id="race-strategy-back-btn"></button>
			<button id="race-strategy-start-btn"></button>
			<div id="race-results-container" data-active-lap-index="1" style="display:none;"></div>
			<div id="race-commentary-log"></div>
			<div id="race-lap-counter"></div>
			<div id="race-leader-display"></div>
			<div id="race-fastest-lap-display"></div>
			<div id="race-latest-commentary"></div>
			<button id="race-pause-btn"></button>
			<button id="race-prev-lap-btn"></button>
			<button id="race-next-lap-btn"></button>
			<button id="race-tab-timing" class="race-tab-btn" data-race-tab="timing"></button>
			<button id="race-tab-qualifying" class="race-tab-btn" data-race-tab="qualifying"></button>
			<button id="race-tab-commentary" class="race-tab-btn" data-race-tab="commentary"></button>
			<button id="race-tab-chart" class="race-tab-btn" data-race-tab="chart"></button>
			<button id="race-tab-laptimes" class="race-tab-btn" data-race-tab="laptimes"></button>
			<div id="race-panel-timing"></div>
			<div id="race-panel-qualifying" style="display:none;"></div>
			<div id="race-panel-commentary" style="display:none;"></div>
			<div id="race-panel-chart" style="display:none;"></div>
			<div id="race-panel-laptimes" style="display:none;"></div>
			<div id="race-results-pole-display"></div>
			<table><tbody id="race-results-qualifying-body"></tbody></table>
			<table><tbody id="race-results-body"></tbody></table>
			<svg id="race-lap-chart-svg"></svg>
			<div id="race-lap-chart-legend"></div>
			<svg id="race-laptime-svg"></svg>
			<div id="race-laptime-legend"></div>
			<select id="race-laptime-driver-1"></select>
			<select id="race-laptime-driver-2"></select>
			<select id="race-laptime-driver-3"></select>
			<select id="race-laptime-driver-4"></select>
			<button id="advance-btn" class="event-active">GO TO RACE</button>
		`;
	});

	it('renders fallback results without lap history and resets race view on exit', () => {
		const nextEventEl = { textContent: 'Next: Monaco Grand Prix - Week 6' };
		const weekEl = { textContent: 'Week 6 1998' };
		enterRaceView(nextEventEl, weekEl);
		expect(document.getElementById('race-view').style.display).toBe('flex');
		expect(document.getElementById('race-event-name').textContent).toBe('Monaco Grand Prix');
		expect(document.getElementById('simulate-race-btn').disabled).toBe(true);
		expect(document.getElementById('simulate-qualifying-btn').disabled).toBe(true);

		renderRaceResults({
			results: [
				{ position: 1, driver_name: 'A', team_name: 'T1', points: 10 },
				{ status: 'DNF', driver_name: 'B', team_name: 'T2', crash_out: true, mechanical_out: false },
				{ status: 'DNF', driver_name: 'C', team_name: 'T3', crash_out: false, mechanical_out: true },
				{ status: 'DNF', driver_name: 'D', team_name: 'T4', crash_out: false, mechanical_out: false },
			],
		});

		const rows = document.getElementById('race-results-body').children;
		expect(rows).toHaveLength(4);
		expect(rows[1].children[7].textContent).toBe('Crash');
		expect(rows[2].children[7].textContent).toBe('Mechanical');
		expect(rows[3].children[7].textContent).toBe('DNF');
		expect(document.getElementById('race-pause-btn').disabled).toBe(true);

		exitRaceView();
		expect(document.getElementById('race-view').style.display).toBe('none');
		expect(document.getElementById('advance-btn').textContent).toBe('ADVANCE');
		expect(document.getElementById('advance-btn').classList.contains('event-active')).toBe(false);
	});

	it('allows manual prev/next stepping and commentary tab switching during lap replay', async () => {
		renderRaceResults({
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
					events: [{ type: 'retirement', lap: 2, driver_name: 'B', reason: 'engine' }],
				},
				{
					lap: 3,
					order: [{ driver_id: 1, position: 1, driver_name: 'C', team_name: 'T1', last_lap_ms: 83200, best_lap_ms: 83000, gap_display: 'LEADER', status: 'FINISHED' }],
					events: [],
				},
			],
			results: [],
		});

		await vi.advanceTimersByTimeAsync(460);
		document.getElementById('race-prev-lap-btn').click();
		expect(document.getElementById('race-pause-btn').textContent).toBe('Resume');
		expect(document.getElementById('race-lap-counter').textContent).toBe('1 / 3');

		document.getElementById('race-next-lap-btn').click();
		expect(document.getElementById('race-lap-counter').textContent).toBe('2 / 3');
		expect(document.getElementById('race-latest-commentary').textContent).toContain('retires with a engine');

		document.getElementById('race-tab-commentary').click();
		expect(document.getElementById('race-panel-commentary').style.display).toBe('');
		expect(document.getElementById('race-panel-timing').style.display).toBe('none');
	});

	it('records lead changes and cancels active autoplay when stepping forward manually', async () => {
		const clearSpy = vi.spyOn(window, 'clearInterval');
		renderRaceResults({
			total_laps: 3,
			lap_history: [
				{
					lap: 1,
					order: [{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83000, best_lap_ms: 83000, gap_display: 'LEADER', status: 'RUNNING' }],
					events: [],
				},
				{
					lap: 2,
					order: [{ driver_id: 2, position: 1, driver_name: 'B', team_name: 'T2', last_lap_ms: 82900, best_lap_ms: 82900, gap_display: 'LEADER', status: 'RUNNING' }],
					events: [],
				},
				{
					lap: 3,
					order: [{ driver_id: 2, position: 1, driver_name: 'B', team_name: 'T2', last_lap_ms: 82800, best_lap_ms: 82800, gap_display: 'LEADER', status: 'FINISHED' }],
					events: [],
				},
			],
			results: [],
		});

		expect(document.getElementById('race-latest-commentary').textContent).toBe('Awaiting the next flashpoint.');
		document.getElementById('race-next-lap-btn').click();
		expect(clearSpy).toHaveBeenCalled();
		expect(document.getElementById('race-lap-counter').textContent).toBe('2 / 3');
		expect(document.getElementById('race-latest-commentary').textContent).toContain('takes the lead');
	});

	it('renders the turn 1 leader commentary event', () => {
		renderRaceResults({
			total_laps: 2,
			qualifying_results: [{ position: 1, driver_name: 'B', team_name: 'T2', best_lap_ms: 82800 }],
			lap_history: [
				{
					lap: 1,
					order: [{ driver_id: 2, position: 1, driver_name: 'B', team_name: 'T2', last_lap_ms: 83000, best_lap_ms: 83000, gap_display: 'LEADER', status: 'RUNNING' }],
					events: [{ type: 'turn_one_leader', lap: 1, driver_id: 2, driver_name: 'B', team_name: 'T2' }],
				},
				{
					lap: 2,
					order: [{ driver_id: 2, position: 1, driver_name: 'B', team_name: 'T2', last_lap_ms: 82900, best_lap_ms: 82900, gap_display: 'LEADER', status: 'FINISHED' }],
					events: [],
				},
			],
			results: [],
		});

		expect(document.getElementById('race-latest-commentary').textContent).toContain('leads out of turn 1');
	});

	it('renders the qualifying weekend panel and enables the race when grid is set', () => {
		renderRaceWeekend({
			circuit_name: 'Monaco Grand Prix',
			circuit_location: 'Monte Carlo',
			circuit_country: 'Monaco',
			laps: 78,
			qualifying_complete: true,
			race_complete: false,
			qualifying_results: [
				{ position: 1, driver_name: 'A', team_name: 'T1', best_lap_ms: 80000 },
				{ position: 2, driver_name: 'B', team_name: 'T2', best_lap_ms: 80200 },
			],
		});

		expect(document.getElementById('race-circuit-display').textContent).toBe('Monaco Grand Prix');
		expect(document.getElementById('race-location-display').textContent).toBe('Monte Carlo, Monaco');
		expect(document.getElementById('race-laps-display').textContent).toBe('78 laps');
		expect(document.getElementById('race-pole-display').textContent).toContain('Pole: A');
		expect(document.getElementById('simulate-qualifying-btn').disabled).toBe(true);
		expect(document.getElementById('simulate-race-btn').disabled).toBe(false);
		expect(document.getElementById('race-qualifying-body').children).toHaveLength(2);
		expect(document.getElementById('race-qualifying-body').children[0].children[4].textContent).toBe('POLE');
		expect(document.getElementById('race-qualifying-body').children[1].children[4].textContent).toBe('+0.200s');
	});

	it('renders a separate pre-race strategy screen from weekend data', () => {
		renderRaceWeekend({
			event_name: 'Monaco Grand Prix',
			circuit_name: 'Monaco Grand Prix',
			circuit_location: 'Monte Carlo',
			circuit_country: 'Monaco',
			laps: 78,
			qualifying_complete: true,
			race_complete: false,
			qualifying_results: [
				{ position: 1, driver_name: 'A', team_name: 'T1', best_lap_ms: 80000 },
				{ position: 2, driver_name: 'B', team_name: 'T1', best_lap_ms: 80200 },
			],
			player_strategies: [
				{ driver_id: 1, driver_name: 'A', planned_stops: 2, planned_pit_laps: [20, 42], grid_position: 1 },
				{ driver_id: 2, driver_name: 'B', planned_stops: 1, planned_pit_laps: [31], grid_position: 2 },
			],
		});

		openRaceStrategyScreen();

		expect(document.getElementById('race-weekend-panel').style.display).toBe('none');
		expect(document.getElementById('race-strategy-panel').style.display).toBe('grid');
		expect(document.getElementById('race-strategy-cards').children).toHaveLength(2);
		expect(document.getElementById('race-strategy-cards').textContent).toContain('Lap 20');
		expect(document.getElementById('race-strategy-start-btn').disabled).toBe(false);

		document.getElementById('race-strategy-stops-1').value = '3';
		expect(collectRaceStrategySelections()).toEqual([
			{ driver_id: 1, planned_stops: 3 },
			{ driver_id: 2, planned_stops: 1 },
		]);

		renderRaceStrategyScreen({
			event_name: 'Monaco Grand Prix',
			qualifying_complete: true,
			race_complete: false,
			player_strategies: [
				{ driver_id: 1, driver_name: 'A', planned_stops: 3, planned_pit_laps: [16, 33, 52], grid_position: 1 },
			],
		});
		expect(document.getElementById('race-strategy-cards').textContent).toContain('Lap 52');
	});

	it('renders qualifying data as a replay tab', () => {
		renderRaceResults({
			total_laps: 1,
			qualifying_results: [
				{ position: 1, driver_name: 'A', team_name: 'T1', best_lap_ms: 80000 },
				{ position: 2, driver_name: 'B', team_name: 'T2', best_lap_ms: 80200 },
			],
			lap_history: [
				{
					lap: 1,
					order: [{ driver_id: 1, position: 1, driver_name: 'A', team_name: 'T1', last_lap_ms: 83000, best_lap_ms: 83000, gap_display: 'LEADER', status: 'FINISHED' }],
					events: [],
				},
			],
			results: [],
		});

		expect(document.getElementById('race-results-qualifying-body').children).toHaveLength(2);
		expect(document.getElementById('race-results-pole-display').textContent).toContain('Pole: A');
		expect(document.getElementById('race-results-qualifying-body').children[0].children[4].textContent).toBe('POLE');
		expect(document.getElementById('race-results-qualifying-body').children[1].children[4].textContent).toBe('+0.200s');
		document.getElementById('race-tab-qualifying').click();
		expect(document.getElementById('race-panel-qualifying').style.display).toBe('');
		expect(document.getElementById('race-panel-timing').style.display).toBe('none');
	});
});
