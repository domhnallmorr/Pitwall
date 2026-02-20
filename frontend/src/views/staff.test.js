import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import StaffView from './staff.js';

describe('StaffView', () => {
	let staffView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="staff-content-drivers"></div>
			<div id="staff-content-workforce" style="display:none;"></div>
			<div id="staff-content-management" style="display:none;"></div>
			<button class="staff-tab-btn active" data-type="drivers">Drivers</button>
			<button class="staff-tab-btn" data-type="workforce">Workforce</button>
			<button class="staff-tab-btn" data-type="management">Management</button>
			<div id="staff-drivers-container"></div>
			<div id="staff-workforce-summary"></div>
			<table><tbody id="staff-workforce-table-body"></tbody></table>
			<div id="staff-management-container"></div>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		staffView = new StaffView();
	});

	it('renders management section with technical and commercial managers and supports tab switch', () => {
		staffView.render({
			team_name: 'Warrick',
			player_workforce: 250,
			teams: [{ name: 'Warrick', country: 'United Kingdom', workforce: 250 }],
			drivers: [],
			technical_director: {
				name: 'Peter Heed',
				age: 52,
				skill: 75,
				contract_length: 5,
				salary: 4800000,
			},
			commercial_manager: {
				name: 'Jace Whitman',
				age: 29,
				skill: 70,
				contract_length: 5,
				salary: 360000,
			},
		});

		const managementBtn = document.querySelector('.staff-tab-btn[data-type="management"]');
		managementBtn.click();

		expect(document.getElementById('staff-content-management').style.display).toBe('block');
		expect(document.getElementById('staff-management-container').innerHTML).toContain('Peter Heed');
		expect(document.getElementById('staff-management-container').innerHTML).toContain('Jace Whitman');
	});
});
