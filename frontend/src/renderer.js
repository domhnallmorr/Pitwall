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
import FinanceView from './views/finance.js';
import FacilitiesView from './views/facilities.js';

// Elements
const titleScreen = document.getElementById('title-screen');
const dashboard = document.getElementById('game-dashboard');
const startBtn = document.getElementById('start-career-btn');
const loadBtn = document.getElementById('load-game-btn');

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
let financeView;
let facilitiesView;

// --- Initialization ---

function init() {
	navigation = new Navigation();
	gridView = new GridView();
	standingsView = new StandingsView();
	calendarView = new CalendarView();
	emailView = new EmailView();
	staffView = new StaffView();
	financeView = new FinanceView();
	facilitiesView = new FacilitiesView();

	setupEventListeners();
	setupIPC();

	// Check if a save file exists
	API.checkSave();
}

function setupEventListeners() {
	startBtn.addEventListener('click', () => {
		console.log("Starting Career...");
		API.startCareer();
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
	const testNoBtn = document.getElementById('test-no-btn');

	if (advanceBtn) {
		advanceBtn.addEventListener('click', () => {
			// Check if it's a test week
			if (advanceBtn.textContent === "GO TO TEST") {
				testModal.style.display = 'flex';
			} else if (advanceBtn.textContent === "GO TO RACE") {
				enterRaceView();
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
				handleGameStart(parsed.data);
			} else if (parsed.type === 'game_loaded' && parsed.status === 'success') {
				handleGameStart(parsed.data);
			} else if (parsed.type === 'save_status') {
				if (parsed.data.has_save) {
					loadBtn.disabled = false;
				}
			} else if (parsed.type === 'grid_data') {
				gridView.render(parsed.data);
			} else if (parsed.type === 'standings_data') {
				standingsView.render(parsed.data);
			} else if (parsed.type === 'calendar_data') {
				calendarView.render(parsed.data);
			} else if (parsed.type === 'week_advanced') {
				updateDashboard(parsed.data);
				// Auto-refresh finance view if it's currently visible
				const financeEl = document.getElementById('finance-view');
				if (financeEl && financeEl.style.display !== 'none') {
					API.getFinance();
				}
			} else if (parsed.type === 'race_result') {
				renderRaceResults(parsed.data);
			} else if (parsed.type === 'email_data') {
				emailView.render(parsed.data);
			} else if (parsed.type === 'email_read') {
				emailView.updateUnreadBadge(parsed.data.unread_count);
			} else if (parsed.type === 'staff_data') {
				staffView.render(parsed.data);
			} else if (parsed.type === 'finance_data') {
				financeView.render(parsed.data);
			} else if (parsed.type === 'facilities_data') {
				facilitiesView.render(parsed.data);
			} else if (parsed.type === 'status') {
				console.log("Status:", parsed.message);
			}
		} catch (e) {
			console.error('Raw Data:', data);
		}
	});
}

function handleGameStart(data) {
	titleScreen.style.display = 'none';
	dashboard.style.display = 'flex';

	teamNameEl.textContent = data.team_name;
	weekEl.textContent = data.week_display;
	nextEventEl.textContent = data.next_event_display;
	if (data.balance !== undefined) updateBalance(data.balance);
}

function updateDashboard(data) {
	weekEl.textContent = data.new_date_display;
	nextEventEl.textContent = data.next_event_display;
	if (data.balance !== undefined) updateBalance(data.balance);

	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn && data.button_text) {
		advanceBtn.textContent = data.button_text;

		// Optional: Add visual cue for event
		if (data.event_active) {
			advanceBtn.classList.add('event-active');
		} else {
			advanceBtn.classList.remove('event-active');
		}
	}
}

function updateBalance(amount) {
	const formatted = '$' + Math.abs(amount).toLocaleString();
	balanceEl.textContent = amount < 0 ? '-' + formatted : formatted;
	balanceEl.className = amount < 0 ? 'balance-info balance-negative' : 'balance-info';
}

// --- Race View Functions ---

function enterRaceView() {
	const raceView = document.getElementById('race-view');
	const event = nextEventEl.textContent; // e.g. "Next: Melbourne Grand Prix - Week 6"
	const raceName = document.getElementById('race-event-name');
	const raceWeek = document.getElementById('race-week-display');

	raceName.textContent = event.replace('Next: ', '').split(' - ')[0] || 'Grand Prix';
	raceWeek.textContent = weekEl.textContent;

	// Reset state
	const simBtn = document.getElementById('simulate-race-btn');
	simBtn.disabled = false;
	simBtn.textContent = 'SIMULATE RACE';
	simBtn.style.display = '';  // Restore visibility
	document.getElementById('race-results-container').style.display = 'none';

	raceView.style.display = 'flex';
}

function renderRaceResults(data) {
	const tbody = document.getElementById('race-results-body');
	const container = document.getElementById('race-results-container');
	const simulateBtn = document.getElementById('simulate-race-btn');

	tbody.innerHTML = '';
	data.results.forEach(r => {
		const row = document.createElement('tr');
		row.innerHTML = `
			<td>${r.position}</td>
			<td>${r.driver_name}</td>
			<td>${r.team_name}</td>
			<td>${r.points > 0 ? r.points : '-'}</td>
		`;
		tbody.appendChild(row);
	});

	simulateBtn.style.display = 'none';
	container.style.display = 'block';
}

function exitRaceView() {
	const raceView = document.getElementById('race-view');
	raceView.style.display = 'none';

	// Update advance button back to ADVANCE (event is now processed)
	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn) {
		advanceBtn.textContent = 'ADVANCE';
		advanceBtn.classList.remove('event-active');
	}
}

// Start
init();
