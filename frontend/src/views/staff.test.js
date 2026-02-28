import { describe, it, expect, beforeEach, vi } from 'vitest';
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

	it('renders replace buttons and disables when contract is 2+ years', () => {
		const onReplace = vi.fn();
		staffView.setReplaceDriverHandler(onReplace);
		staffView.render({
			team_name: 'Warrick',
			player_workforce: 250,
			teams: [{ name: 'Warrick', country: 'United Kingdom', workforce: 250 }],
			drivers: [
				{ id: 1, name: 'Driver A', age: 30, country: 'UK', speed: 80, wage: 1000, pay_driver: false, contract_length: 2 },
				{ id: 2, name: 'Driver B', age: 24, country: 'DE', speed: 70, wage: 1000, pay_driver: false, contract_length: 1 },
			],
			technical_director: null,
			commercial_manager: null,
		});

		const buttons = document.querySelectorAll('.staff-replace-btn');
		expect(buttons.length).toBe(2);
		expect(buttons[0].disabled).toBe(true);
		expect(buttons[1].disabled).toBe(false);

		buttons[1].click();
		expect(onReplace).toHaveBeenCalledWith(2);
	});
});
