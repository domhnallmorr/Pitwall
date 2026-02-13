/**
 * Main Renderer
 * Entry point for the frontend logic.
 */

import API from './api.js';
import Navigation from './views/navigation.js';
import GridView from './views/grid.js';
import StandingsView from './views/standings.js';
import CalendarView from './views/calendar.js';

// Elements
const titleScreen = document.getElementById('title-screen');
const dashboard = document.getElementById('game-dashboard');
const startBtn = document.getElementById('start-career-btn');

// Dashboard Info
const teamNameEl = document.getElementById('team-name');
const dateEl = document.getElementById('current-date');

// Modules
let navigation;
let gridView;
let standingsView;
let calendarView;

// --- Initialization ---

function init() {
	navigation = new Navigation();
	gridView = new GridView();
	standingsView = new StandingsView();
	calendarView = new CalendarView();

	setupEventListeners();
	setupIPC();
}

function setupEventListeners() {
	startBtn.addEventListener('click', () => {
		console.log("Starting Career...");
		API.startCareer();
	});

	// Debug
	document.getElementById('ping-btn')?.addEventListener('click', API.ping);
	document.getElementById('roster-btn')?.addEventListener('click', API.loadRoster);
}

function setupIPC() {
	API.onData((data) => {
		console.log('Python Data:', data);
		try {
			const parsed = JSON.parse(data);

			if (parsed.type === 'game_started' && parsed.status === 'success') {
				handleGameStart(parsed.data);
			} else if (parsed.type === 'grid_data') {
				gridView.render(parsed.data);
			} else if (parsed.type === 'standings_data') {
				standingsView.render(parsed.data);
			} else if (parsed.type === 'calendar_data') {
				calendarView.render(parsed.data);
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
	dateEl.textContent = `${data.current_date} ${data.year}`;
}

// Start
init();
