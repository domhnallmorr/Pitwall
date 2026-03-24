/**
 * Main Renderer
 * Entry point for the frontend logic.
 */

import API from './api.js';
import Navigation from './views/navigation.js';
import GridView from './views/grid.js';
import StandingsView from './views/standings.js';
import CalendarView from './views/calendar.js';
import EmailView from './views/email.js';
import StaffView from './views/staff.js';
import DriverView from './views/driver.js';
import DriverMarketView from './views/driver_market.js';
import CarView from './views/car.js';
import FinanceView from './views/finance.js';
import FacilitiesView from './views/facilities.js';
import { renderLayoutPartials } from './layout/partials.js';
import {
	enterRaceView,
	exitRaceView,
	handleGameStart,
	openDriverProfile,
	refreshVisibleViews,
	renderRaceResults,
	showTeamSelect,
	updateDashboard,
} from './renderer/helpers.js';

// Elements
const titleScreen = document.getElementById('title-screen');
const dashboard = document.getElementById('game-dashboard');
const startBtn = document.getElementById('start-career-btn');
const loadBtn = document.getElementById('load-game-btn');
const titleStartActions = document.getElementById('title-start-actions');
const teamSelectScreen = document.getElementById('team-select-screen');
const teamSelectButtons = document.getElementById('team-select-buttons');

// Dashboard Info
const teamNameEl = document.getElementById('team-name');
const weekEl = document.getElementById('current-week');
const nextEventEl = document.getElementById('next-event');
const balanceEl = document.getElementById('team-balance');

// Modules
let navigation;
let gridView;
let standingsView;
let calendarView;
let emailView;
let staffView;
let driverView;
let driverMarketView;
let carView;
let financeView;
let facilitiesView;

const TEAM_OPTIONS = [
	'Warrick',
	'Ferano',
	'Benedetti',
	'McAlister',
	'Joyce',
	'Pascal',
	'Schweizer',
	'Swords',
	'Strathmore',
	'Tarnwell',
	'Marchetti',
];

// --- Initialization ---

function init() {
	renderLayoutPartials();

	navigation = new Navigation();
	gridView = new GridView();
	standingsView = new StandingsView();
	calendarView = new CalendarView();
	emailView = new EmailView();
	staffView = new StaffView();
	staffView.setReplaceDriverHandler((driverId) => API.getReplacementCandidates(driverId));
	staffView.setReplaceCommercialManagerHandler((managerId) => API.getManagerReplacementCandidates(managerId));
	staffView.setReplaceTechnicalDirectorHandler((directorId) => API.getTechnicalDirectorReplacementCandidates(directorId));
	staffView.setUpdateWorkforceHandler((workforce) => API.updateWorkforce(workforce));
	driverView = new DriverView();
	driverMarketView = new DriverMarketView();
	driverMarketView.setBackHandler(() => {
		if (driverMarketView.marketType === 'title_sponsor') {
			if (navigation) navigation.showView('finance');
			API.getFinance();
			return;
		}
		if (navigation) navigation.showView('staff');
		API.getStaff();
	});
	driverMarketView.setSignHandler((outgoingId, incomingId, marketType = 'driver') => {
		if (marketType === 'commercial_manager') {
			API.replaceCommercialManager(outgoingId, incomingId);
			return;
		}
		if (marketType === 'technical_director') {
			API.replaceTechnicalDirector(outgoingId, incomingId);
			return;
		}
		if (marketType === 'title_sponsor') {
			API.replaceTitleSponsor(outgoingId, incomingId);
			return;
		}
		API.replaceDriver(outgoingId, incomingId);
	});
	carView = new CarView();
	carView.setStartDevelopmentHandler((developmentType) => API.startCarDevelopment(developmentType));
	carView.setRepairWearHandler((wearPoints) => API.repairCarWear(wearPoints));
	financeView = new FinanceView();
	financeView.setReplaceTitleSponsorHandler((sponsorName) => API.getTitleSponsorReplacementCandidates(sponsorName));
	facilitiesView = new FacilitiesView();
	facilitiesView.setPreviewHandler((points, years) => API.previewFacilitiesUpgrade(points, years));
	facilitiesView.setStartUpgradeHandler((points, years) => API.startFacilitiesUpgrade(points, years));
	gridView.setYearRequestHandler((year) => API.getGrid(year));
	gridView.setDriverSelectHandler((name) => openDriverProfile(name, navigation, API));
	standingsView.setDriverSelectHandler((name) => openDriverProfile(name, navigation, API));

	setupEventListeners();
	setupIPC();

	// Check if a save file exists
	API.checkSave();
}

function setupEventListeners() {
	startBtn.addEventListener('click', () => {
		showTeamSelect({
			titleStartActions,
			teamSelectScreen,
			teamSelectButtons,
			teamOptions: TEAM_OPTIONS,
			api: API,
		});
	});

	loadBtn.addEventListener('click', () => {
		console.log("Loading Game...");
		API.loadGame();
	});

	// Debug
	document.getElementById('ping-btn')?.addEventListener('click', API.ping);
	document.getElementById('roster-btn')?.addEventListener('click', API.loadRoster);

	// Advance Button
	const advanceBtn = document.getElementById('advance-btn');
	const testModal = document.getElementById('test-session-modal');
	const testKmModal = document.getElementById('test-km-modal');
	const testNoBtn = document.getElementById('test-no-btn');
	const testYesBtn = document.getElementById('test-yes-btn');
	const testKmInput = document.getElementById('test-km-input');
	const testKmValue = document.getElementById('test-km-value');
	const testKmCost = document.getElementById('test-km-cost');
	const testKmCancelBtn = document.getElementById('test-km-cancel-btn');
	const testKmConfirmBtn = document.getElementById('test-km-confirm-btn');

	const updateTestKmPreview = () => {
		if (!testKmInput || !testKmValue || !testKmCost) return;
		const kms = Number(testKmInput.value || 0);
		testKmValue.textContent = kms.toLocaleString();
		testKmCost.textContent = `$${(kms * 1400).toLocaleString()}`;
	};

	if (advanceBtn) {
		advanceBtn.addEventListener('click', () => {
			// Check if it's a test week
			if (advanceBtn.textContent === "GO TO TEST") {
				testModal.style.display = 'flex';
			} else if (advanceBtn.textContent === "GO TO RACE") {
				enterRaceView(nextEventEl, weekEl);
			} else {
				console.log("Advancing Week...");
				API.advanceWeek();
			}
		});
	}

	// Modal Controls
	if (testNoBtn) {
		testNoBtn.addEventListener('click', () => {
			testModal.style.display = 'none';
			API.skipEvent(); // Skip test, stay in week, update button
		});
	}

	if (testYesBtn) {
		testYesBtn.addEventListener('click', () => {
			testModal.style.display = 'none';
			if (testKmModal) testKmModal.style.display = 'flex';
			updateTestKmPreview();
		});
	}

	if (testKmInput) {
		testKmInput.addEventListener('input', updateTestKmPreview);
	}

	if (testKmCancelBtn) {
		testKmCancelBtn.addEventListener('click', () => {
			if (testKmModal) testKmModal.style.display = 'none';
			if (testModal) testModal.style.display = 'flex';
		});
	}

	if (testKmConfirmBtn) {
		testKmConfirmBtn.addEventListener('click', () => {
			const kms = Number(testKmInput?.value || 0);
			if (testKmModal) testKmModal.style.display = 'none';
			API.attendTest(kms);
		});
	}

	// Race View Controls
	const simulateBtn = document.getElementById('simulate-race-btn');
	const returnBtn = document.getElementById('return-dashboard-btn');

	if (simulateBtn) {
		simulateBtn.addEventListener('click', () => {
			console.log("Simulating Race...");
			simulateBtn.disabled = true;
			simulateBtn.textContent = "SIMULATING...";
			API.simulateRace();
		});
	}

	if (returnBtn) {
		returnBtn.addEventListener('click', () => {
			exitRaceView();
		});
	}
}

function setupIPC() {
	API.onData((data) => {
		console.log('Python Data:', data);
		try {
			const parsed = JSON.parse(data);

			if (parsed.type === 'game_started' && parsed.status === 'success') {
				handleGameStart({
					data: parsed.data,
					titleScreen,
					dashboard,
					gridView,
					teamNameEl,
					weekEl,
					nextEventEl,
					balanceEl,
					emailView,
					api: API,
				});
			} else if (parsed.type === 'game_loaded' && parsed.status === 'success') {
				handleGameStart({
					data: parsed.data,
					titleScreen,
					dashboard,
					gridView,
					teamNameEl,
					weekEl,
					nextEventEl,
					balanceEl,
					emailView,
					api: API,
				});
			} else if (parsed.type === 'save_status') {
				if (parsed.data.has_save) {
					loadBtn.disabled = false;
				}
			} else if (parsed.type === 'grid_data') {
				gridView.render(parsed.data, parsed.year);
			} else if (parsed.type === 'standings_data') {
				standingsView.render(parsed.data);
				gridView.setDriverCountryMap(parsed.data.drivers);
			} else if (parsed.type === 'calendar_data') {
				calendarView.render(parsed.data);
			} else if (parsed.type === 'week_advanced') {
				updateDashboard({
					data: parsed.data,
					weekEl,
					nextEventEl,
					balanceEl,
					gridView,
					api: API,
				});
				refreshVisibleViews({ gridView, driverView, api: API });
				API.getEmails(); // Keep unread badge/messages in sync with new events.
				// Auto-refresh finance view if it's currently visible
				const financeEl = document.getElementById('finance-view');
				if (financeEl && financeEl.style.display !== 'none') {
					API.getFinance();
				}
			} else if (parsed.type === 'race_result') {
				renderRaceResults(parsed.data);
				refreshVisibleViews({ gridView, driverView, api: API });
				API.getFinance();
			} else if (parsed.type === 'email_data') {
				emailView.render(parsed.data);
			} else if (parsed.type === 'email_read') {
				emailView.updateUnreadBadge(parsed.data.unread_count);
			} else if (parsed.type === 'staff_data') {
				staffView.render(parsed.data);
			} else if (parsed.type === 'workforce_updated') {
				if (parsed.status === 'success') {
					API.getStaff();
					API.getFinance();
					API.getCar();
					API.getEmails();
				}
			} else if (parsed.type === 'replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'manager_replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'title_sponsor_replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'driver_replaced') {
				if (navigation) navigation.showView('staff');
				API.getStaff();
				API.getGrid(gridView.getActiveYear());
				API.getGrid(gridView.baseYear + 1);
				API.getEmails();
			} else if (parsed.type === 'commercial_manager_replaced') {
				if (navigation) navigation.showView('staff');
				API.getStaff();
				API.getGrid(gridView.getActiveYear());
				API.getGrid(gridView.baseYear + 1);
				API.getEmails();
			} else if (parsed.type === 'technical_director_replaced') {
				if (navigation) navigation.showView('staff');
				API.getStaff();
				API.getGrid(gridView.getActiveYear());
				API.getGrid(gridView.baseYear + 1);
				API.getEmails();
			} else if (parsed.type === 'title_sponsor_replaced') {
				if (navigation) navigation.showView('finance');
				API.getFinance();
				API.getGrid(gridView.getActiveYear());
				API.getGrid(gridView.baseYear + 1);
				API.getEmails();
			} else if (parsed.type === 'driver_data') {
				driverView.render(parsed.data);
			} else if (parsed.type === 'car_data') {
				carView.render(parsed.data);
			} else if (parsed.type === 'car_development_started') {
				if (parsed.status === 'success') {
					API.getCar();
					API.getFinance();
					API.getEmails();
				}
			} else if (parsed.type === 'car_wear_repaired') {
				if (parsed.status === 'success') {
					API.getCar();
					API.getFinance();
					API.getEmails();
				}
			} else if (parsed.type === 'finance_data') {
				financeView.render(parsed.data);
			} else if (parsed.type === 'facilities_data') {
				facilitiesView.render(parsed.data);
			} else if (parsed.type === 'facilities_upgrade_preview') {
				facilitiesView.renderPreview(parsed.data, parsed.status, parsed.message);
			} else if (parsed.type === 'facilities_upgrade_started') {
				if (parsed.status === 'success') {
					facilitiesView.closeUpgradeModal();
					API.getFacilities();
					API.getFinance();
					API.getEmails();
				} else {
					facilitiesView.renderPreview(null, 'error', parsed.message || 'Unable to start facilities upgrade');
				}
			} else if (parsed.type === 'status') {
				console.log("Status:", parsed.message);
			}
		} catch (e) {
			console.error('Raw Data:', data);
		}
	});
}

// Start
init();
