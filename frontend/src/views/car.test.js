import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import CarView from './car.js';

describe('CarView', () => {
	let carView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="car-content-comparison"></div>
			<div id="car-content-development" style="display:none;"></div>
			<div id="car-content-construction" style="display:none;"></div>
			<div id="car-content-chassis" style="display:none;"></div>
			<div id="car-development-current-speed"></div>
			<div id="car-development-status"></div>
			<div id="car-garage-race-assignments-status"></div>
			<div id="car-garage-mechanics-status"></div>
			<div id="car-spares-widget"></div>
			<div id="car-construction-build-card"></div>
			<table><tbody id="car-table-body"></tbody></table>
			<table><tbody id="car-development-table-body"></tbody></table>
			<table><tbody id="car-chassis-table-body"></tbody></table>
			<button class="car-tab-btn active" data-type="comparison"></button>
			<button class="car-tab-btn" data-type="development"></button>
			<button class="car-tab-btn" data-type="construction"></button>
			<button class="car-tab-btn" data-type="chassis"></button>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		carView = new CarView();
	});

	const sampleData = {
		teams: [
			{ name: 'Warrick', country: 'United Kingdom', car_speed: 80, engine_power: 60 },
			{ name: 'Ferano', country: 'Italy', car_speed: 84, engine_power: 72 },
		],
		player_car_speed: 80,
		player_spares: 6,
		construction: {
			spares: {
				available: 6,
				max: 10,
				build_cost: 52500,
				construction_usage_percent: 36,
				construction_capacity_remaining: 64,
				engineering_required_percentage: 18,
				engineering_required_staff: 11,
				engineering_staff_available: 61,
				can_build: true,
				blocking_reason: null,
			},
		},
		maintenance: {
			mechanics_usage_percent: 22,
			mechanics_capacity_remaining: 78,
			mechanics_staff_available: 58,
			mechanics_required_percent_per_spare: 22,
			can_repair: true,
		},
		player_drivers: [
			{ id: 1, name: 'John Newhouse' },
			{ id: 2, name: 'Henrik Friedrich' },
		],
		player_chassis: [
			{ id: 1, name: 'Chassis 1', wear: 5, assigned_to_test: false, assigned_driver_id: 1, assigned_driver_name: 'John Newhouse', mechanical_fail_probability: 0.01 },
			{ id: 2, name: 'Chassis 2', wear: 9, assigned_to_test: false, assigned_driver_id: 2, assigned_driver_name: 'Henrik Friedrich', mechanical_fail_probability: 0.018 },
			{ id: 3, name: 'Chassis 3', wear: 0, assigned_to_test: true, assigned_driver_id: null, assigned_driver_name: null, mechanical_fail_probability: 0 },
		],
		player_development: { active: false },
		development_catalog: [],
	};

	it('renders chassis rows with integrated controls', () => {
		carView.render(sampleData);
		carView.setActiveTab('chassis');

		expect(document.getElementById('car-content-chassis').style.display).toBe('block');
		expect(document.getElementById('car-chassis-table-body').textContent).toContain('Chassis 1');
		expect(document.getElementById('car-chassis-table-body').textContent).toContain('John Newhouse');
		expect(document.querySelectorAll('.car-chassis-test-radio')).toHaveLength(3);
		expect(document.querySelectorAll('.car-chassis-assignment-select')).toHaveLength(3);
		expect(document.querySelectorAll('.car-chassis-repair-btn')).toHaveLength(3);
		expect(document.querySelector('.car-chassis-repair-spares[data-chassis-id="1"]').textContent).toContain('0 spare sets');
		expect(document.getElementById('car-garage-race-assignments-status').textContent).toContain('Race chassis assigned');
		expect(document.getElementById('car-garage-mechanics-status').textContent).toContain('78% remaining');
		carView.setActiveTab('construction');
		expect(document.getElementById('car-content-construction').style.display).toBe('block');
		expect(document.getElementById('car-spares-widget').textContent).toContain('Available Spares');
		expect(document.getElementById('car-spares-widget').textContent).toContain('6 / 10 sets');
		expect(document.querySelectorAll('#car-spares-widget .car-availability-block.is-filled')).toHaveLength(6);
		expect(document.getElementById('car-construction-build-card').textContent).toContain('Build Spare Set');
		expect(document.getElementById('car-construction-build-card').textContent).toContain('$52,500');
		expect(document.getElementById('car-construction-build-card').textContent).toContain('36%');
		expect(document.getElementById('car-construction-build-card').textContent).toContain('64%');
	});

	it('wires row-level chassis controls to handlers', () => {
		const onSetTestChassis = vi.fn();
		const onSetRaceChassisAssignments = vi.fn();
		const onRepairChassisWear = vi.fn();
		const onBuildSpareSet = vi.fn();
		carView.setTestChassisHandler(onSetTestChassis);
		carView.setRaceChassisAssignmentsHandler(onSetRaceChassisAssignments);
		carView.setRepairChassisWearHandler(onRepairChassisWear);
		carView.setBuildSpareSetHandler(onBuildSpareSet);
		carView.render(sampleData);

		const testRadio = document.querySelector('.car-chassis-test-radio[value="2"]');
		testRadio.checked = true;
		testRadio.dispatchEvent(new window.Event('change'));
		expect(onSetTestChassis).toHaveBeenCalledWith(2);

		const assignmentSelects = document.querySelectorAll('.car-chassis-assignment-select');
		assignmentSelects[0].value = '2';
		assignmentSelects[0].dispatchEvent(new window.Event('change'));
		assignmentSelects[2].value = '1';
		assignmentSelects[2].dispatchEvent(new window.Event('change'));
		expect(onSetRaceChassisAssignments).toHaveBeenCalledWith(3, 1);

		const slider = document.querySelector('.car-chassis-repair-slider[data-chassis-id="2"]');
		slider.value = '4';
		slider.dispatchEvent(new window.Event('input'));
		expect(document.querySelector('.car-chassis-repair-spares[data-chassis-id="2"]').textContent).toContain('Est. 1 spare set');
		expect(document.querySelector('.car-chassis-repair-mechanics[data-chassis-id="2"]').textContent).toContain('Est. 22% mechanics');
		document.querySelector('.car-chassis-repair-btn[data-chassis-id="2"]').click();
		expect(onRepairChassisWear).toHaveBeenCalledWith(2, 4);

		document.getElementById('car-build-spare-set-btn').click();
		expect(onBuildSpareSet).toHaveBeenCalledTimes(1);
	});

	it('updates the spares widget immediately from a repair result', () => {
		carView.render(sampleData);

		carView.applyChassisWearRepairResult({ spares_after: 4 });
		carView.applyChassisWearRepairResult({ mechanics_usage_percent_after: 55 });

		expect(document.getElementById('car-spares-widget').textContent).toContain('4 / 10 sets');
		expect(document.querySelectorAll('#car-spares-widget .car-availability-block.is-filled')).toHaveLength(4);
		expect(document.getElementById('car-garage-mechanics-status').textContent).toContain('45% remaining');
	});
});
