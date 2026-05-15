import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import CarView from './car.js';

describe('CarView', () => {
	let carView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="car-content-comparison"></div>
			<div id="car-content-development" style="display:none;"></div>
			<div id="car-content-tyres" style="display:none;"></div>
			<div id="car-content-construction" style="display:none;"></div>
			<div id="car-content-chassis" style="display:none;"></div>
			<div id="car-tyres-suppliers"></div>
			<div id="car-development-current-speed"></div>
			<div id="car-development-status"></div>
			<div id="car-garage-race-assignments-status"></div>
			<div id="car-garage-mechanics-status"></div>
			<div id="car-spares-widget"></div>
			<div id="car-construction-projects-card"></div>
			<div id="car-construction-build-card"></div>
			<table><tbody id="car-table-body"></tbody></table>
			<table><tbody id="car-development-table-body"></tbody></table>
			<table><tbody id="car-chassis-table-body"></tbody></table>
			<button class="car-tab-btn active" data-type="comparison"></button>
			<button class="car-tab-btn" data-type="development"></button>
			<button class="car-tab-btn" data-type="tyres"></button>
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
		player_setup_knowledge: 42,
		player_spares: 6,
		tyres: {
			suppliers: [
				{
					name: 'Greatday',
					country: 'USA',
					resources: 88,
					innovation: 82,
					reliability: 90,
					is_player_supplier: true,
					compounds: [
						{ name: 'Hard', grip: 67, wear: 93, stiffness: 87 },
						{ name: 'Medium', grip: 77, wear: 79, stiffness: 67 },
						{ name: 'Soft', grip: 88, wear: 64, stiffness: 47 },
					],
				},
				{
					name: 'Spanrock',
					country: 'Japan',
					resources: 86,
					innovation: 91,
					reliability: 84,
					is_player_supplier: false,
					compounds: [
						{ name: 'Hard', grip: 66, wear: 89, stiffness: 84 },
						{ name: 'Medium', grip: 78, wear: 77, stiffness: 64 },
						{ name: 'Soft', grip: 90, wear: 60, stiffness: 44 },
					],
				},
			],
		},
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
		player_development: {
			active: false,
			stages: [
				{ key: 'design', label: 'Design', progress: 0, completed: false },
				{ key: 'cfd', label: 'CFD Simulation', progress: 0, completed: false },
				{ key: 'model', label: 'Model Design', progress: 0, completed: false },
				{ key: 'wind_tunnel', label: 'Wind Tunnel', progress: 0, completed: false },
			],
		},
		development_catalog: [],
	};

	it('renders stage-based chassis development and wires actions', () => {
		const onStartDevelopment = vi.fn();
		const onFinishDevelopmentStage = vi.fn();
		const onSetDevelopmentAllocation = vi.fn();
		carView.setStartDevelopmentHandler(onStartDevelopment);
		carView.setFinishDevelopmentStageHandler(onFinishDevelopmentStage);
		carView.setDevelopmentAllocationHandler(onSetDevelopmentAllocation);

		carView.render(sampleData);
		carView.setActiveTab('development');

		expect(document.getElementById('car-content-development').style.display).toBe('block');
		const currentSpeed = document.getElementById('car-development-current-speed');
		expect(currentSpeed.textContent).toContain('Setup Knowledge:');
		expect(currentSpeed.textContent).not.toContain('42/100');
		const setupRating = currentSpeed.querySelectorAll('.car-speed-rating')[1];
		expect(setupRating.querySelectorAll('.car-speed-block')).toHaveLength(10);
		expect(setupRating.querySelectorAll('.car-speed-block.is-filled')).toHaveLength(5);
		expect(document.getElementById('car-development-status').textContent).toContain('No active chassis design project');
		expect(document.getElementById('car-development-table-body').textContent).toContain('Design');
		document.querySelector('.car-dev-btn').click();
		expect(onStartDevelopment).toHaveBeenCalledWith('current_year');

		carView.render({
			...sampleData,
			player_development: {
				active: true,
				name: 'Current Chassis Upgrade',
				current_stage_index: 0,
				current_stage_label: 'Design',
				assigned_designers: 63,
				allocation_percent: 100,
				weekly_cost: 0,
				projected_speed_delta: 2,
				risk: 'Medium',
				can_finish_stage: true,
				finish_action_label: 'Finish Stage',
				stages: [
					{ key: 'design', label: 'Design', progress: 3, completed: false },
					{ key: 'cfd', label: 'CFD Simulation', progress: 0, completed: false },
					{ key: 'model', label: 'Model Design', progress: 0, completed: false },
					{ key: 'wind_tunnel', label: 'Wind Tunnel', progress: 0, completed: false },
				],
			},
		});
		expect(document.getElementById('car-development-status').textContent).toContain('Current Chassis Upgrade: 100%, Design');
		expect(document.querySelectorAll('.car-development-progress-block.is-filled')).toHaveLength(3);
		const slider = document.querySelector('.car-dev-allocation-slider[data-dev-scope="current_year"]');
		slider.value = '55';
		slider.dispatchEvent(new window.Event('input'));
		expect(document.querySelector('.car-dev-allocation-value[data-dev-scope="current_year"]').textContent).toBe('55%');
		slider.dispatchEvent(new window.Event('change'));
		expect(onSetDevelopmentAllocation).toHaveBeenCalledWith('current_year', 55);
		document.querySelector('.car-dev-finish-stage-btn').click();
		expect(onFinishDevelopmentStage).toHaveBeenCalledWith('current_year');
	});

	it('caps allocation sliders to the backend-reported available percentage', () => {
		carView.render({
			...sampleData,
			player_development: {
				active: true,
				projects: {
					current_year: {
						active: true,
						scope: 'current_year',
						name: 'Current Chassis Upgrade',
						allocation_percent: 70,
						available_allocation_percent: 70,
						assigned_designers: 44,
						weekly_cost: 0,
						stages: [{ key: 'design', label: 'Design', progress: 1, completed: false }],
					},
					next_year: {
						active: true,
						scope: 'next_year',
						name: '1999 Chassis',
						allocation_percent: 30,
						available_allocation_percent: 30,
						assigned_designers: 19,
						weekly_cost: 0,
						stages: [{ key: 'design', label: 'Design', progress: 1, completed: false }],
					},
				},
			},
		});

		expect(document.querySelector('.car-dev-allocation-slider[data-dev-scope="current_year"]').max).toBe('70');
		expect(document.querySelector('.car-dev-allocation-slider[data-dev-scope="next_year"]').max).toBe('30');
		expect(document.getElementById('car-development-table-body').textContent).toContain('Max available: 30%');
	});

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
		carView.setActiveTab('tyres');
		expect(document.getElementById('car-content-tyres').style.display).toBe('block');
		expect(document.getElementById('car-tyres-suppliers').textContent).toContain('Greatday');
		expect(document.getElementById('car-tyres-suppliers').textContent).toContain('Current Supplier');
		expect(document.getElementById('car-tyres-suppliers').textContent).toContain('Soft');
		expect(document.getElementById('car-tyres-suppliers').textContent).toContain('Spanrock');
		expect(document.querySelectorAll('.car-tyre-compound-table .car-speed-rating').length).toBeGreaterThan(0);
		carView.setActiveTab('construction');
		expect(document.getElementById('car-content-construction').style.display).toBe('block');
		expect(document.getElementById('car-spares-widget').textContent).toContain('Available Spares');
		expect(document.getElementById('car-spares-widget').textContent).toContain('6 / 10 sets');
		expect(document.querySelectorAll('#car-spares-widget .car-availability-block.is-filled')).toHaveLength(6);
		expect(document.getElementById('car-construction-build-card').textContent).toContain('Build Spare Set');
		expect(document.getElementById('car-construction-projects-card').textContent).toContain('Chassis Construction');
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

	it('renders queued construction projects and wires start/allocation controls', () => {
		const onStartConstruction = vi.fn();
		const onSetConstructionAllocation = vi.fn();
		carView.setStartConstructionHandler(onStartConstruction);
		carView.setConstructionAllocationHandler(onSetConstructionAllocation);
		carView.render({
			...sampleData,
			construction: {
				...sampleData.construction,
				projects: {
					projects: {
						current_year: {
							active: false,
							can_start: true,
							scope: 'current_year',
							name: 'Current Chassis Upgrade',
							total_cost: 20000,
							paid: 0,
							progress: 0,
							progress_required: 10,
							speed_delta: 1,
							available_allocation_percent: 100,
							target_week_range: [2, 4],
						},
						next_year: {
							active: true,
							can_start: false,
							scope: 'next_year',
							name: '1999 Chassis',
							total_cost: 1000000,
							paid: 125000,
							progress: 3,
							progress_required: 24,
							units_built: 0,
							units_required: 2,
							allocation_percent: 40,
							available_allocation_percent: 100,
							assigned_engineers: 24,
							estimated_weeks: 12,
							target_week_range: [4, 8],
						},
					},
				},
			},
		});

		expect(document.getElementById('car-construction-projects-card').textContent).toContain('Current Chassis Upgrade');
		expect(document.getElementById('car-construction-projects-card').textContent).toContain('$20,000');
		expect(document.getElementById('car-construction-projects-card').textContent).toContain('4-8 weeks');
		expect(document.getElementById('car-construction-projects-card').textContent).toContain('12 weeks');
		document.querySelector('.car-construction-start-btn[data-construction-scope="current_year"]').click();
		expect(onStartConstruction).toHaveBeenCalledWith('current_year');

		const slider = document.querySelector('.car-construction-allocation-slider[data-construction-scope="next_year"]');
		slider.value = '55';
		slider.dispatchEvent(new window.Event('input'));
		expect(document.querySelector('.car-construction-allocation-value[data-construction-scope="next_year"]').textContent).toBe('55%');
		slider.dispatchEvent(new window.Event('change'));
		expect(onSetConstructionAllocation).toHaveBeenCalledWith('next_year', 55);
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
