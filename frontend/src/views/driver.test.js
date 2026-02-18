import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import DriverView from './driver.js';

describe('DriverView', () => {
	let driverView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="driver-profile-title"></div>
			<div id="driver-profile-container"></div>
			<div id="driver-season-results-container"></div>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		driverView = new DriverView();
	});

	it('renders core stats and season result podium classes', () => {
		driverView.render({
			name: 'John Newhouse',
			team_name: 'Warrick',
			age: 27,
			country: 'Canada',
			speed: 84,
			race_starts: 33,
			wins: 11,
			points: 10,
			wage: 9600000,
			pay_driver: false,
			season_results: [
				{ round: 1, country: 'Australia', position: 1 },
				{ round: 2, country: 'Brazil', position: 2 },
				{ round: 3, country: 'Argentina', position: 3 },
			],
		});

		expect(document.getElementById('driver-profile-title').textContent).toBe('John Newhouse');
		expect(document.getElementById('driver-profile-container').innerHTML).toContain('Race Starts');
		expect(document.getElementById('driver-profile-container').innerHTML).toContain('Wins');

		const seasonHtml = document.getElementById('driver-season-results-container').innerHTML;
		expect(seasonHtml).toContain('driver-season-table');
		expect(document.querySelectorAll('.driver-season-pos-cell.is-gold').length).toBe(1);
		expect(document.querySelectorAll('.driver-season-pos-cell.is-silver').length).toBe(1);
		expect(document.querySelectorAll('.driver-season-pos-cell.is-bronze').length).toBe(1);
	});
});
