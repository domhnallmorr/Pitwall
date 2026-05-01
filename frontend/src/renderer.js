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
import CommercialView from './views/commercial.js';
import FacilitiesView from './views/facilities.js';
import { renderLayoutPartials } from './layout/partials.js';
import {
	collectRaceStrategySelections,
	enterRaceView,
	exitRaceView,
	handleGameStart,
	openRaceStrategyScreen,
	openDriverProfile,
	refreshVisibleViews,
	renderHomeView,
	renderRaceResults,
	renderRaceStrategyScreen,
	renderRaceWeekend,
	setRacePlaybackCompleteHandler,
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
const gameOverModal = document.getElementById('game-over-modal');
const gameOverModalTitle = document.getElementById('game-over-modal-title');
const gameOverModalBody = document.getElementById('game-over-modal-body');
const gameOverModalCloseBtn = document.getElementById('game-over-modal-close-btn');
const driverProfileBackBtn = document.getElementById('driver-profile-back-btn');

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
let commercialView;
let facilitiesView;
let previousDriverView = 'staff';
let pendingGameOverModalTimeout = null;
let pendingGameOverModalPayload = null;

function showCurrentSaveGameOver() {
	showGameOverModal({
		title: 'Game Over',
		body: 'This career save is already over due to insolvency.',
	});
}

function refreshGridYears() {
	API.getGrid(gridView.getActiveYear());
	API.getGrid(gridView.baseYear + 1);
}

function refreshGridYearsAndEmails() {
	refreshGridYears();
	API.getEmails();
}

function activateCommercialTab(tabName) {
	if (navigation) {
		navigation.activateView('commercial');
		navigation.showView('commercial');
	}
	commercialView.showTab(tabName);
}

function renderCommercialNegotiation(parsed, render, tabName, errorMessage) {
	if (parsed.status === 'error') {
		window.alert(parsed.message || errorMessage);
		return;
	}
	render(parsed.data);
	activateCommercialTab(tabName);
}

function refreshDriverMarketOutcome(viewName) {
	if (navigation) navigation.showView(viewName);
	if (viewName === 'staff') {
		API.getStaff();
	} else if (viewName === 'finance') {
		API.getFinance();
	}
	refreshGridYearsAndEmails();
}

function refreshCarRelatedViews() {
	API.getCar();
	API.getFinance();
	API.getEmails();
}

function handleGameLifecycleSuccess(data) {
	handleGameStart({
		data,
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
	if (data?.game_over) {
		showCurrentSaveGameOver();
	}
}

function showGameOverModal({ title = 'Game Over', body = 'The career has ended.' } = {}) {
	if (pendingGameOverModalTimeout) {
		window.clearTimeout(pendingGameOverModalTimeout);
		pendingGameOverModalTimeout = null;
	}
	pendingGameOverModalPayload = null;
	if (gameOverModalTitle) gameOverModalTitle.textContent = title;
	if (gameOverModalBody) gameOverModalBody.textContent = body;
	if (gameOverModal) gameOverModal.style.display = 'flex';
}

function hideGameOverModal() {
	if (pendingGameOverModalTimeout) {
		window.clearTimeout(pendingGameOverModalTimeout);
		pendingGameOverModalTimeout = null;
	}
	if (gameOverModal) gameOverModal.style.display = 'none';
}

function goBackFromDriverProfile() {
	if (!navigation) return;
	const targetView = previousDriverView || 'staff';
	navigation.showView(targetView);
	if (targetView === 'home') {
		API.getHome();
	} else if (targetView === 'grid') {
		API.getStandings();
		API.getGrid(gridView?.getActiveYear?.());
	} else if (targetView === 'staff') {
		API.getStaff();
	} else if (targetView === 'standings') {
		API.getStandings();
	} else if (targetView === 'driver-market') {
		// Keep existing market content visible; no fetch needed here.
	} else if (targetView === 'finance') {
		API.getFinance();
	} else if (targetView === 'commercial') {
		API.getFinance();
	} else if (targetView === 'calendar') {
		API.getCalendar();
	} else if (targetView === 'email') {
		API.getEmails();
	} else if (targetView === 'car') {
		API.getCar();
	} else if (targetView === 'facilities') {
		API.getFacilities();
	}
}

function openDriverProfileFromCurrentView(name) {
	if (!name) return;
	const currentView = navigation?.currentView;
	if (currentView && currentView !== 'driver') {
		previousDriverView = currentView;
	}
	openDriverProfile(name, navigation, API);
}

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
	staffView.setDriverSelectHandler((name) => openDriverProfileFromCurrentView(name));
	staffView.setReplaceCommercialManagerHandler((managerId) => API.getManagerReplacementCandidates(managerId));
	staffView.setReplaceTechnicalDirectorHandler((directorId) => API.getTechnicalDirectorReplacementCandidates(directorId));
	driverView = new DriverView();
	driverMarketView = new DriverMarketView();
	driverMarketView.setBackHandler(() => {
		if (driverMarketView.marketType === 'title_sponsor' || driverMarketView.marketType === 'engine_supplier' || driverMarketView.marketType === 'tyre_supplier') {
			if (navigation) navigation.showView('finance');
			API.getFinance();
			return;
		}
		if (navigation) navigation.showView('staff');
		API.getStaff();
	});
	driverMarketView.setSignHandler((outgoingId, incomingId, marketType = 'driver', offer = null) => {
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
		if (marketType === 'engine_supplier') {
			API.replaceEngineSupplier(outgoingId, incomingId);
			return;
		}
		if (marketType === 'tyre_supplier') {
			API.replaceTyreSupplier(outgoingId, incomingId);
			return;
		}
		if (offer) {
			API.offerDriver(outgoingId, incomingId, offer.salary, offer.contract_length);
			return;
		}
		API.replaceDriver(outgoingId, incomingId);
	});
	carView = new CarView();
	carView.setStartDevelopmentHandler((developmentType) => API.startCarDevelopment(developmentType));
	carView.setTestChassisHandler((chassisId) => API.setTestChassis(chassisId));
	carView.setRaceChassisAssignmentsHandler((driver1ChassisId, driver2ChassisId) => API.setRaceChassisAssignments(driver1ChassisId, driver2ChassisId));
	carView.setRepairChassisWearHandler((chassisId, wearPoints) => API.repairChassisWear(chassisId, wearPoints));
	carView.setBuildSpareSetHandler(() => API.buildSpareSet());
	financeView = new FinanceView();
	financeView.setReplaceTitleSponsorHandler(() => API.getTitleSponsorNegotiationMarket());
	financeView.setReplaceEngineSupplierHandler(() => API.getEngineNegotiationMarket());
	financeView.setReplaceTyreSupplierHandler((supplierName) => API.getTyreSupplierReplacementCandidates(supplierName));
	commercialView = new CommercialView();
	commercialView.setStartTitleSponsorNegotiationHandler((sponsorId) => API.startTitleSponsorNegotiation(sponsorId));
	commercialView.setUpdateTitleSponsorNegotiationStaffHandler((assignedStaff) => API.updateTitleSponsorNegotiationStaff(assignedStaff));
	commercialView.setSignTitleSponsorNegotiatedDealHandler(() => API.signTitleSponsorNegotiatedDeal());
	commercialView.setBookTitleSponsorHospitalityHandler(() => API.bookTitleSponsorHospitality());
	commercialView.setStartEngineNegotiationHandler((supplierId) => API.startEngineNegotiation(supplierId));
	commercialView.setUpdateEngineNegotiationStaffHandler((assignedStaff) => API.updateEngineNegotiationStaff(assignedStaff));
	commercialView.setSignEngineNegotiatedDealHandler((tier) => API.signEngineNegotiatedDeal(tier));
	commercialView.setBookEngineNegotiationHospitalityHandler(() => API.bookEngineNegotiationHospitality());
	facilitiesView = new FacilitiesView();
	facilitiesView.setPreviewHandler((points, years) => API.previewFacilitiesUpgrade(points, years));
	facilitiesView.setStartUpgradeHandler((points, years) => API.startFacilitiesUpgrade(points, years));
	gridView.setYearRequestHandler((year) => API.getGrid(year));
	gridView.setDriverSelectHandler((name) => openDriverProfileFromCurrentView(name));
	standingsView.setDriverSelectHandler((name) => openDriverProfileFromCurrentView(name));

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
				API.getRaceWeekend();
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

	if (gameOverModalCloseBtn) {
		gameOverModalCloseBtn.addEventListener('click', hideGameOverModal);
	}

	if (driverProfileBackBtn) {
		driverProfileBackBtn.addEventListener('click', goBackFromDriverProfile);
	}

	// Race View Controls
	const qualifyingBtn = document.getElementById('simulate-qualifying-btn');
	const simulateBtn = document.getElementById('simulate-race-btn');
	const strategyOpenBtn = document.getElementById('open-race-strategy-btn');
	const strategyBackBtn = document.getElementById('race-strategy-back-btn');
	const strategyStartBtn = document.getElementById('race-strategy-start-btn');
	const returnBtn = document.getElementById('return-dashboard-btn');

	if (qualifyingBtn) {
		qualifyingBtn.addEventListener('click', () => {
			console.log("Simulating Qualifying...");
			qualifyingBtn.disabled = true;
			qualifyingBtn.textContent = "RUNNING...";
			API.simulateQualifying();
		});
	}

	if (simulateBtn) {
		simulateBtn.addEventListener('click', () => {
			openRaceStrategyScreen();
		});
	}

	if (strategyOpenBtn) {
		strategyOpenBtn.addEventListener('click', () => {
			openRaceStrategyScreen();
		});
	}

	if (strategyBackBtn) {
		strategyBackBtn.addEventListener('click', () => {
			renderRaceWeekend();
		});
	}

	if (strategyStartBtn) {
		strategyStartBtn.addEventListener('click', () => {
			console.log("Simulating Race...");
			strategyStartBtn.disabled = true;
			strategyStartBtn.textContent = "SIMULATING...";
			API.simulateRace();
		});
	}

	document.addEventListener('change', (event) => {
		const target = event.target;
		if (
			!(target instanceof HTMLElement) ||
			(!target.classList.contains('race-strategy-stop-select') && !target.classList.contains('race-strategy-tyre-select'))
		) {
			return;
		}
		API.setRaceStrategy(collectRaceStrategySelections());
	});

	document.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement) || !target.classList.contains('race-strategy-regenerate-btn')) {
			return;
		}
		API.setRaceStrategy(collectRaceStrategySelections());
	});

	if (returnBtn) {
		returnBtn.addEventListener('click', () => {
			exitRaceView();
			if (pendingGameOverModalPayload) {
				showGameOverModal(pendingGameOverModalPayload);
			}
		});
	}
}

function setupIPC() {
	API.onData((data) => {
		console.log('Python Data:', data);
		try {
			const parsed = JSON.parse(data);

			if (parsed.type === 'game_started' && parsed.status === 'success') {
				handleGameLifecycleSuccess(parsed.data);
			} else if (parsed.type === 'game_loaded' && parsed.status === 'success') {
				handleGameLifecycleSuccess(parsed.data);
			} else if (parsed.type === 'save_status') {
				if (parsed.data.has_save) {
					loadBtn.disabled = false;
				}
			} else if (parsed.type === 'grid_data') {
				gridView.render(parsed.data, parsed.year);
			} else if (parsed.type === 'home_data') {
				renderHomeView(parsed.data);
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
				API.getEmails();
				// Auto-refresh finance view if it's currently visible
				const financeEl = document.getElementById('finance-view');
				if (financeEl && financeEl.style.display !== 'none') {
					API.getFinance();
				}
			} else if (parsed.type === 'race_result') {
				renderRaceResults(parsed.data);
				refreshVisibleViews({ gridView, driverView, api: API });
				API.getFinance();
			} else if (parsed.type === 'game_over') {
				const modalPayload = {
					title: 'Game Over',
					body: parsed.data?.message || 'The career has ended due to insolvency.',
				};
				pendingGameOverModalPayload = modalPayload;
				const showBankruptcyModal = () => {
					showGameOverModal(modalPayload);
				};
				if (parsed.data?.race_result) {
					const lapHistory = Array.isArray(parsed.data.race_result.lap_history) ? parsed.data.race_result.lap_history : [];
					if (lapHistory.length > 0) {
						setRacePlaybackCompleteHandler(showBankruptcyModal);
						pendingGameOverModalTimeout = window.setTimeout(
							showBankruptcyModal,
							Math.max(500, lapHistory.length * 500),
						);
					}
					renderRaceResults(parsed.data.race_result);
					if (lapHistory.length <= 1) {
						showBankruptcyModal();
					}
				} else {
					showBankruptcyModal();
				}
				if (parsed.data?.summary) {
					updateDashboard({
						data: parsed.data.summary,
						weekEl,
						nextEventEl,
						balanceEl,
						gridView,
						api: API,
					});
				}
				refreshVisibleViews({ gridView, driverView, api: API });
				API.getFinance();
				API.getEmails();
			} else if (parsed.type === 'race_weekend') {
				renderRaceWeekend(parsed.data);
			} else if (parsed.type === 'qualifying_result') {
				renderRaceWeekend(parsed.data);
			} else if (parsed.type === 'race_strategy_updated') {
				renderRaceStrategyScreen(parsed.data);
			} else if (parsed.type === 'email_data') {
				emailView.render(parsed.data);
			} else if (parsed.type === 'email_read') {
				emailView.updateUnreadBadge(parsed.data.unread_count);
			} else if (parsed.type === 'staff_data') {
				staffView.render(parsed.data);
			} else if (parsed.type === 'replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'manager_replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'title_sponsor_replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'title_sponsor_negotiation_market' || parsed.type === 'title_sponsor_negotiation_updated') {
				renderCommercialNegotiation(
					parsed,
					(data) => commercialView.renderTitleSponsorNegotiation(data),
					'title-sponsor',
					'Unable to update title sponsor negotiation.',
				);
			} else if (parsed.type === 'engine_supplier_replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'engine_negotiation_market' || parsed.type === 'engine_negotiation_updated') {
				renderCommercialNegotiation(
					parsed,
					(data) => commercialView.renderEngineNegotiation(data),
					'engine',
					'Unable to update engine negotiation.',
				);
			} else if (parsed.type === 'tyre_supplier_replacement_candidates') {
				driverMarketView.render(parsed.data);
				if (navigation) navigation.showView('driver-market');
			} else if (parsed.type === 'driver_replaced') {
				refreshDriverMarketOutcome('staff');
			} else if (parsed.type === 'driver_offer_result') {
				const didShowResult = driverMarketView?.showOfferResult?.(parsed.data || {}, () => {
					if (parsed.data?.accepted) {
						refreshDriverMarketOutcome('staff');
					}
				});
				if (!didShowResult) {
					window.alert(parsed.data?.message || 'Driver offer processed.');
					if (parsed.data?.accepted) {
						refreshDriverMarketOutcome('staff');
					}
				}
			} else if (parsed.type === 'commercial_manager_replaced') {
				refreshDriverMarketOutcome('staff');
			} else if (parsed.type === 'technical_director_replaced') {
				refreshDriverMarketOutcome('staff');
			} else if (parsed.type === 'title_sponsor_replaced') {
				refreshDriverMarketOutcome('finance');
			} else if (parsed.type === 'title_sponsor_negotiation_signed') {
				activateCommercialTab('title-sponsor');
				API.getFinance();
				refreshGridYearsAndEmails();
			} else if (parsed.type === 'engine_supplier_replaced') {
				refreshDriverMarketOutcome('finance');
			} else if (parsed.type === 'engine_negotiation_signed') {
				activateCommercialTab('engine');
				API.getFinance();
				refreshGridYearsAndEmails();
			} else if (parsed.type === 'tyre_supplier_replaced') {
				refreshDriverMarketOutcome('finance');
			} else if (parsed.type === 'driver_data') {
				driverView.render(parsed.data);
			} else if (parsed.type === 'car_data') {
				carView.render(parsed.data);
			} else if (parsed.type === 'car_development_started') {
				if (parsed.status === 'success') {
					refreshCarRelatedViews();
				}
			} else if (parsed.type === 'test_chassis_updated' || parsed.type === 'race_chassis_assignments_updated' || parsed.type === 'chassis_wear_repaired' || parsed.type === 'spare_set_built') {
				if (parsed.status === 'success') {
					if (parsed.type === 'chassis_wear_repaired') {
						carView.applyChassisWearRepairResult(parsed.data);
					}
					refreshCarRelatedViews();
				}
			} else if (parsed.type === 'finance_data') {
				financeView.render(parsed.data);
				commercialView.render(parsed.data);
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
