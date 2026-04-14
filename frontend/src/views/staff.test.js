import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import StaffView from './staff.js';

describe('StaffView', () => {
	let staffView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="staff-content-drivers"></div>
			<div id="staff-content-operational" style="display:none;"></div>
			<div id="staff-content-management" style="display:none;"></div>
			<div id="staff-content-commercial" style="display:none;"></div>
			<button class="staff-tab-btn active" data-type="drivers">Drivers</button>
			<button class="staff-tab-btn" data-type="management">Management</button>
			<button class="staff-tab-btn" data-type="design">Design</button>
			<button class="staff-tab-btn" data-type="engineering">Engineering</button>
			<button class="staff-tab-btn" data-type="mechanics">Mechanics</button>
			<button class="staff-tab-btn" data-type="commercial">Commercial</button>
			<div id="staff-drivers-container"></div>
			<div id="staff-operational-summary"></div>
			<div id="staff-operational-payroll"></div>
			<table><tbody id="staff-operational-table-body"></tbody></table>
			<div id="staff-management-container"></div>
			<div id="staff-commercial-summary"></div>
			<div id="staff-commercial-payroll"></div>
			<table><tbody id="staff-commercial-table-body"></tbody></table>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		staffView = new StaffView();
	});

	it('renders management section with technical and commercial managers and supports tab switch', () => {
		staffView.render({
			team_name: 'Warrick',
			factory_size: 4,
			player_workforce: 250,
			player_commercial_staff: 49,
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
			factory_size: 4,
			player_workforce: 250,
			player_commercial_staff: 49,
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

	it('renders design department breakdown and payroll details', () => {
		staffView.render({
			team_name: 'Warrick',
			factory_size: 4,
			player_workforce: 200,
			player_commercial_staff: 49,
			workforce_limits: { min: 0, max: 320 },
			commercial_staff_limits: { min: 0, max: 80 },
			projected_workforce_race_cost: 320000,
			projected_workforce_annual_cost: 5600000,
			operational_staff: {
				design_count: 70,
				engineering_count: 65,
				mechanics_count: 65,
				design_annual_avg_wage: 25000,
				engineering_annual_avg_wage: 22000,
				mechanics_annual_avg_wage: 20000,
			},
			projected_commercial_staff_race_cost: 57647,
			projected_commercial_staff_annual_cost: 980000,
			commercial_staff_annual_avg_wage: 20000,
			races_in_season: 17,
			teams: [{ name: 'Warrick', country: 'United Kingdom', workforce: 200 }],
			drivers: [],
			technical_director: null,
			commercial_manager: null,
		});

		document.querySelector('.staff-tab-btn[data-type="design"]').click();
		expect(document.getElementById('staff-content-operational').style.display).toBe('block');
		expect(document.getElementById('staff-operational-payroll').textContent).toContain('Projected payroll');
		expect(document.getElementById('staff-commercial-payroll').textContent).toContain('Projected payroll');
		expect(document.getElementById('staff-operational-summary').textContent).toContain('design staff');
		expect(document.getElementById('staff-operational-summary').textContent).toContain('320');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('Average');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('70');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('$25,000');
		expect(document.getElementById('staff-commercial-summary').textContent).toContain('80');
	});

	it('switches operational tabs between design engineering and mechanics', () => {
		staffView.render({
			team_name: 'Ferano',
			factory_size: 4,
			player_workforce: 194,
			workforce_limits: { min: 0, max: 320 },
			races_in_season: 16,
			operational_staff: {
				design_count: 68,
				engineering_count: 64,
				mechanics_count: 62,
				design_annual_avg_wage: 25000,
				engineering_annual_avg_wage: 22000,
				mechanics_annual_avg_wage: 20000,
			},
			drivers: [],
			technical_director: null,
			commercial_manager: null,
			teams: [],
		});

		document.querySelector('.staff-tab-btn[data-type="engineering"]').click();
		expect(document.getElementById('staff-operational-summary').textContent).toContain('engineering staff');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('64');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('$22,000');

		document.querySelector('.staff-tab-btn[data-type="mechanics"]').click();
		expect(document.getElementById('staff-operational-summary').textContent).toContain('mechanics staff');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('62');
		expect(document.getElementById('staff-operational-table-body').textContent).toContain('$20,000');
	});

	it('covers guard branches and empty states', () => {
		expect(staffView.getSpeedRating('bad')).toBe(1);
		expect(staffView.getSpeedRating(999)).toBe(5);
		expect(staffView.getWorkforceRating(0, 0)).toBe(1);
		expect(staffView.renderSpeedBlocks(0)).toContain('Speed rating 1 out of 5');
		expect(staffView.renderSkillBlocks(100)).toContain('Skill rating 5 out of 5');

		staffView.render({
			drivers: [],
			technical_director: null,
			commercial_manager: null,
			teams: [],
		});

		expect(document.getElementById('staff-drivers-container').textContent).toContain('No drivers assigned');
		expect(document.getElementById('staff-management-container').textContent).toContain('No management staff assigned');
		expect(document.getElementById('staff-operational-summary').textContent).toContain('Your team design staff');
		expect(document.getElementById('staff-commercial-summary').textContent).toContain('Your team commercial staff');
	});

	it('renders commercial tab content', () => {
		staffView.render({
			team_name: 'Schweizer',
			factory_size: 3,
			player_workforce: 131,
			player_commercial_staff: 49,
			commercial_staff_limits: { min: 0, max: 60 },
			projected_commercial_staff_race_cost: 57647,
			projected_commercial_staff_annual_cost: 980000,
			commercial_staff_annual_avg_wage: 20000,
			races_in_season: 17,
			drivers: [],
			technical_director: null,
			commercial_manager: null,
			teams: [],
		});

		document.querySelector('.staff-tab-btn[data-type="commercial"]').click();
		expect(document.getElementById('staff-content-commercial').style.display).toBe('block');
		expect(document.getElementById('staff-commercial-table-body').textContent).toContain('Average');
		expect(document.getElementById('staff-commercial-table-body').textContent).toContain('49');
		expect(document.getElementById('staff-commercial-table-body').textContent).toContain('$20,000');
		expect(document.getElementById('staff-commercial-summary').textContent).toContain('60');
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

	it('opens driver profile when clicking a driver name', () => {
		const onSelect = vi.fn();
		staffView.setDriverSelectHandler(onSelect);
		staffView.render({
			drivers: [
				{ id: 1, name: 'Driver A', age: 30, country: 'UK', speed: 80, wage: 1000, pay_driver: false, contract_length: 1 },
			],
			technical_director: null,
			commercial_manager: null,
			teams: [],
		});

		document.querySelector('.staff-driver-link').click();
		expect(onSelect).toHaveBeenCalledWith('Driver A');
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
