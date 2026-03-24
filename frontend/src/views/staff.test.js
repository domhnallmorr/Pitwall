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
			<div id="staff-workforce-editor"></div>
			<input id="staff-workforce-input" type="number" />
			<button id="staff-workforce-apply-btn">Update</button>
			<div id="staff-workforce-payroll"></div>
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

	it('calls workforce update handler with selected value', () => {
		const onUpdate = vi.fn();
		staffView.setUpdateWorkforceHandler(onUpdate);
		staffView.render({
			team_name: 'Warrick',
			player_workforce: 200,
			workforce_limits: { min: 0, max: 250 },
			projected_workforce_race_cost: 320000,
			projected_workforce_annual_cost: 5600000,
			races_in_season: 17,
			teams: [{ name: 'Warrick', country: 'United Kingdom', workforce: 200 }],
			drivers: [],
			technical_director: null,
			commercial_manager: null,
		});

		const input = document.getElementById('staff-workforce-input');
		const apply = document.getElementById('staff-workforce-apply-btn');
		input.value = '215';
		apply.click();

		expect(onUpdate).toHaveBeenCalledWith(215);
		expect(document.getElementById('staff-workforce-payroll').textContent).toContain('Projected payroll');
	});

	it('covers guard branches and empty states', () => {
		expect(staffView.getSpeedRating('bad')).toBe(1);
		expect(staffView.getSpeedRating(999)).toBe(5);
		expect(staffView.getWorkforceRating(0, 0)).toBe(1);
		expect(staffView.renderSpeedBlocks(0)).toContain('Speed rating 1 out of 5');
		expect(staffView.renderSkillBlocks(100)).toContain('Skill rating 5 out of 5');

		const apply = document.getElementById('staff-workforce-apply-btn');
		const input = document.getElementById('staff-workforce-input');
		input.value = 'not-a-number';
		apply.click();

		staffView.render({
			drivers: [],
			technical_director: null,
			commercial_manager: null,
			teams: [],
		});

		expect(document.getElementById('staff-drivers-container').textContent).toContain('No drivers assigned');
		expect(document.getElementById('staff-management-container').textContent).toContain('No management staff assigned');
		expect(document.getElementById('staff-workforce-summary').textContent).toContain('Your team workforce');
	});

	it('handles management replace edge cases and management-only rendering', () => {
		const onReplaceManager = vi.fn();
		const onReplaceDirector = vi.fn();
		staffView.setReplaceCommercialManagerHandler(onReplaceManager);
		staffView.setReplaceTechnicalDirectorHandler(onReplaceDirector);

		staffView.render({
			team_name: 'Warrick',
			player_workforce: 180,
			teams: [],
			drivers: [],
			technical_director: {
				id: 6,
				name: 'Tech One',
				age: 45,
				country: 'UK',
				skill: 82,
				contract_length: 1,
				salary: 500000,
			},
			commercial_manager: {
				id: 7,
				name: 'Manager One',
				age: 38,
				country: 'US',
				skill: 77,
				contract_length: 1,
				salary: 320000,
			},
		});

		const directorBtn = document.querySelector('.staff-replace-technical-director-btn');
		expect(directorBtn.disabled).toBe(false);
		directorBtn.click();
		expect(onReplaceDirector).toHaveBeenCalledWith(6);

		staffView.setReplaceTechnicalDirectorHandler(null);
		directorBtn.click();
		expect(onReplaceDirector).toHaveBeenCalledTimes(1);

		directorBtn.setAttribute('data-director-id', 'bad');
		staffView.setReplaceTechnicalDirectorHandler(onReplaceDirector);
		directorBtn.click();
		expect(onReplaceDirector).toHaveBeenCalledTimes(1);

		const managerBtn = document.querySelector('.staff-replace-manager-btn');
		expect(managerBtn.disabled).toBe(false);
		managerBtn.click();
		expect(onReplaceManager).toHaveBeenCalledWith(7);

		staffView.setReplaceCommercialManagerHandler(null);
		managerBtn.click();
		expect(onReplaceManager).toHaveBeenCalledTimes(1);

		managerBtn.setAttribute('data-manager-id', 'bad');
		staffView.setReplaceCommercialManagerHandler(onReplaceManager);
		managerBtn.click();
		expect(onReplaceManager).toHaveBeenCalledTimes(1);
	});

	it('handles driver replace edge cases and pay driver rendering', () => {
		const onReplace = vi.fn();
		staffView.setReplaceDriverHandler(onReplace);
		staffView.render({
			drivers: [
				{ id: 1, name: 'Driver A', age: 30, country: 'UK', speed: 80, wage: -250000, pay_driver: true, contract_length: 1 },
			],
			technical_director: null,
			commercial_manager: null,
			teams: [],
		});

		expect(document.getElementById('staff-drivers-container').textContent).toContain('Pay Driver');
		const driverBtn = document.querySelector('.staff-replace-btn');
		driverBtn.click();
		expect(onReplace).toHaveBeenCalledWith(1);

		staffView.setReplaceDriverHandler(null);
		driverBtn.click();
		expect(onReplace).toHaveBeenCalledTimes(1);

		driverBtn.setAttribute('data-driver-id', 'nope');
		staffView.setReplaceDriverHandler(onReplace);
		driverBtn.click();
		expect(onReplace).toHaveBeenCalledTimes(1);
	});

	it('disables replace buttons when a pending replacement exists', () => {
		staffView.render({
			drivers: [
				{ id: 1, name: 'Driver A', age: 30, country: 'UK', speed: 80, wage: 1000, pay_driver: false, contract_length: 1, pending_replacement: true },
			],
			technical_director: {
				id: 6,
				name: 'Tech One',
				age: 45,
				country: 'UK',
				skill: 82,
				contract_length: 1,
				pending_replacement: true,
				salary: 500000,
			},
			commercial_manager: {
				id: 7,
				name: 'Manager One',
				age: 38,
				country: 'US',
				skill: 77,
				contract_length: 1,
				pending_replacement: true,
				salary: 320000,
			},
			teams: [],
		});

		expect(document.querySelector('.staff-replace-btn').disabled).toBe(true);
		expect(document.querySelector('.staff-replace-technical-director-btn').disabled).toBe(true);
		expect(document.querySelector('.staff-replace-manager-btn').disabled).toBe(true);
	});
});
