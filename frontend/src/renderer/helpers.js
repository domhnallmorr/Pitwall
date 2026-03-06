export function updateBalance(balanceEl, amount) {
	const formatted = '$' + Math.abs(amount).toLocaleString();
	balanceEl.textContent = amount < 0 ? '-' + formatted : formatted;
	balanceEl.className = amount < 0 ? 'balance-info balance-negative' : 'balance-info';
}

export function handleGameStart({
	data,
	titleScreen,
	dashboard,
	gridView,
	teamNameEl,
	weekEl,
	nextEventEl,
	balanceEl,
	emailView,
	api,
}) {
	titleScreen.style.display = 'none';
	dashboard.style.display = 'flex';
	gridView.setSeasonBase(data.year);

	teamNameEl.textContent = data.team_name;
	weekEl.textContent = data.week_display;
	nextEventEl.textContent = data.next_event_display;
	if (data.balance !== undefined) updateBalance(balanceEl, data.balance);
	if (data.unread_count !== undefined) emailView.updateUnreadBadge(data.unread_count);

	api.getStandings();
	api.getGrid(data.year);
	api.getGrid(data.year + 1);
}

export function updateDashboard({ data, weekEl, nextEventEl, balanceEl, gridView, api }) {
	weekEl.textContent = data.new_date_display;
	nextEventEl.textContent = data.next_event_display;
	if (data.balance !== undefined) updateBalance(balanceEl, data.balance);

	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn && data.button_text) {
		advanceBtn.textContent = data.button_text;
		if (data.event_active) advanceBtn.classList.add('event-active');
		else advanceBtn.classList.remove('event-active');
	}

	if (data.year && Number(data.year) !== gridView.baseYear) {
		gridView.setSeasonBase(data.year);
		api.getGrid(data.year);
		api.getGrid(data.year + 1);
	}
}

export function showTeamSelect({ titleStartActions, teamSelectScreen, teamSelectButtons, teamOptions, api }) {
	if (titleStartActions) titleStartActions.style.display = 'none';
	if (!teamSelectScreen || !teamSelectButtons) return;
	teamSelectButtons.innerHTML = '';

	teamOptions.forEach((teamName) => {
		const btn = document.createElement('button');
		btn.className = 'team-select-btn';
		btn.textContent = teamName;
		btn.addEventListener('click', () => {
			console.log(`Starting Career as ${teamName}...`);
			api.startCareer(teamName);
		});
		teamSelectButtons.appendChild(btn);
	});

	teamSelectScreen.style.display = 'block';
}

export function refreshVisibleViews({ gridView, driverView, api }) {
	const gridEl = document.getElementById('grid-view');
	if (gridEl && gridEl.style.display !== 'none') api.getGrid(gridView.getActiveYear());

	const staffEl = document.getElementById('staff-view');
	if (staffEl && staffEl.style.display !== 'none') api.getStaff();

	const carEl = document.getElementById('car-view');
	if (carEl && carEl.style.display !== 'none') api.getCar();

	const standingsEl = document.getElementById('standings-view');
	if (standingsEl && standingsEl.style.display !== 'none') api.getStandings();

	const driverEl = document.getElementById('driver-view');
	if (driverEl && driverEl.style.display !== 'none' && driverView?.currentDriverName) {
		api.getDriver(driverView.currentDriverName);
	}

	const financeEl = document.getElementById('finance-view');
	if (financeEl && financeEl.style.display !== 'none') api.getFinance();

	const facilitiesEl = document.getElementById('facilities-view');
	if (facilitiesEl && facilitiesEl.style.display !== 'none') api.getFacilities();
}

export function openDriverProfile(driverName, navigation, api) {
	if (!driverName) return;
	if (navigation) navigation.showView('driver');
	api.getDriver(driverName);
}

export function enterRaceView(nextEventEl, weekEl) {
	const raceView = document.getElementById('race-view');
	const event = nextEventEl.textContent;
	const raceName = document.getElementById('race-event-name');
	const raceWeek = document.getElementById('race-week-display');

	raceName.textContent = event.replace('Next: ', '').split(' - ')[0] || 'Grand Prix';
	raceWeek.textContent = weekEl.textContent;

	const simBtn = document.getElementById('simulate-race-btn');
	simBtn.disabled = false;
	simBtn.textContent = 'SIMULATE RACE';
	simBtn.style.display = '';
	document.getElementById('race-results-container').style.display = 'none';

	raceView.style.display = 'flex';
}

export function renderRaceResults(data) {
	const tbody = document.getElementById('race-results-body');
	const container = document.getElementById('race-results-container');
	const simulateBtn = document.getElementById('simulate-race-btn');

	tbody.innerHTML = '';
	data.results.forEach((r) => {
		const positionLabel = Number.isInteger(r.position) ? r.position : (r.status || 'DNF');
		let statusLabel = 'Finished';
		if (!Number.isInteger(r.position)) {
			if (r.crash_out) statusLabel = 'Crash';
			else if (r.mechanical_out) statusLabel = 'Mechanical';
			else statusLabel = r.status || 'DNF';
		}
		const row = document.createElement('tr');
		row.innerHTML = `
			<td>${positionLabel}</td>
			<td>${r.driver_name}</td>
			<td>${r.team_name}</td>
			<td>${statusLabel}</td>
			<td>${r.points > 0 ? r.points : '-'}</td>
		`;
		tbody.appendChild(row);
	});

	simulateBtn.style.display = 'none';
	container.style.display = 'block';
}

export function exitRaceView() {
	const raceView = document.getElementById('race-view');
	raceView.style.display = 'none';

	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn) {
		advanceBtn.textContent = 'ADVANCE';
		advanceBtn.classList.remove('event-active');
	}
}
