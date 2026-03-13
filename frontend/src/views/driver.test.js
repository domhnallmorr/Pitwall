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

	it('renders DNF for non-classified season results', () => {
		driverView.render({
			name: 'Jamie Brenton',
			team_name: 'Warrick',
			age: 20,
			country: 'United Kingdom',
			speed: 80,
			race_starts: 1,
			wins: 0,
			points: 0,
			wage: 0,
			pay_driver: false,
			season_results: [
				{ round: 1, country: 'Australia', position: null, status: 'DNF' },
			],
		});

		const seasonHtml = document.getElementById('driver-season-results-container').textContent;
		expect(seasonHtml).toContain('DNF');
	});

	it('renders driver not found state and clears season results', () => {
		driverView.render({
			name: 'Existing Driver',
			season_results: [{ round: 1, country: 'Australia', position: 1 }],
		});

		driverView.render(null);

		expect(document.getElementById('driver-profile-title').textContent).toBe('Driver Profile');
		expect(document.getElementById('driver-profile-container').textContent).toContain('Driver not found');
		expect(document.getElementById('driver-season-results-container').innerHTML).toBe('');
		expect(driverView.currentDriverName).toBe(null);
	});

	it('renders free agent, pay driver, empty season, and speed clamps', () => {
		expect(driverView.getSpeedRating('bad')).toBe(1);
		expect(driverView.getSpeedRating(500)).toBe(5);
		expect(driverView.renderSpeedBlocks(0)).toContain('Speed rating 1 out of 5');

		driverView.render({
			name: 'Test Driver',
			team_name: '',
			age: 19,
			country: 'Ireland',
			speed: 0,
			race_starts: 0,
			wins: 0,
			points: 0,
			wage: -500000,
			pay_driver: true,
			season_results: [],
		});

		const profileHtml = document.getElementById('driver-profile-container').innerHTML;
		expect(profileHtml).toContain('Free Agent');
		expect(profileHtml).toContain('Pay Driver');
		expect(document.getElementById('driver-season-results-container').textContent).toContain('No race results recorded this season yet');
	});
});
