import { formatLapTime, renderLapChart, renderLaptimeChart } from './race_charts.js';

const RACE_AUTOPLAY_INTERVAL_MS = 450;
let raceAutoplayTimer = null;
let raceAutoplayData = null;
let raceAutoplayLapIndex = 0;
let raceAutoplayPaused = false;
let currentRaceWeekendData = null;
let onRacePlaybackComplete = null;

function getRaceElements() {
	return {
		raceView: document.getElementById('race-view'),
		weekendPanel: document.getElementById('race-weekend-panel'),
		strategyPanel: document.getElementById('race-strategy-panel'),
		resultsContainer: document.getElementById('race-results-container'),
		raceName: document.getElementById('race-event-name'),
		raceWeek: document.getElementById('race-week-display'),
		circuitDisplay: document.getElementById('race-circuit-display'),
		locationDisplay: document.getElementById('race-location-display'),
		lapsDisplay: document.getElementById('race-laps-display'),
		poleDisplay: document.getElementById('race-pole-display'),
		statusText: document.getElementById('race-weekend-status'),
		statusChip: document.getElementById('race-status-chip'),
		qualifyingBody: document.getElementById('race-qualifying-body'),
		qualifyingBtn: document.getElementById('simulate-qualifying-btn'),
		simBtn: document.getElementById('simulate-race-btn'),
		commentaryLog: document.getElementById('race-commentary-log'),
		lapCounter: document.getElementById('race-lap-counter'),
		leaderDisplay: document.getElementById('race-leader-display'),
		fastestLapDisplay: document.getElementById('race-fastest-lap-display'),
		latestCommentary: document.getElementById('race-latest-commentary'),
		pauseBtn: document.getElementById('race-pause-btn'),
		prevBtn: document.getElementById('race-prev-lap-btn'),
		nextBtn: document.getElementById('race-next-lap-btn'),
		timingTab: document.getElementById('race-tab-timing'),
		qualifyingTab: document.getElementById('race-tab-qualifying'),
		commentaryTab: document.getElementById('race-tab-commentary'),
		chartTab: document.getElementById('race-tab-chart'),
		laptimesTab: document.getElementById('race-tab-laptimes'),
		qualifyingResultsBody: document.getElementById('race-results-qualifying-body'),
		qualifyingPoleDisplay: document.getElementById('race-results-pole-display'),
		timingBody: document.getElementById('race-results-body'),
		eventDisplay: document.getElementById('race-strategy-event-display'),
		strategyCards: document.getElementById('race-strategy-cards'),
		strategyStartBtn: document.getElementById('race-strategy-start-btn'),
	};
}

function setRaceStatus(statusText, statusChip, message, chipText, chipClass) {
	if (statusText) statusText.textContent = message;
	if (statusChip) {
		statusChip.textContent = chipText;
		statusChip.className = `race-status-chip ${chipClass}`;
	}
}

function renderQualifyingTable(tbody, qualifyingResults, emptyMessage) {
	if (!tbody) return;
	tbody.innerHTML = '';
	if (!qualifyingResults.length) {
		tbody.innerHTML = `<tr class="race-qualifying-placeholder"><td colspan="5">${emptyMessage}</td></tr>`;
		return;
	}

	const poleLapMs = qualifyingResults[0].best_lap_ms;
	qualifyingResults.forEach((row) => {
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${row.position}</td>
			<td>${row.driver_name}</td>
			<td>${row.team_name}</td>
			<td>${formatLapTime(row.best_lap_ms)}</td>
			<td>${formatQualifyingGap(row.best_lap_ms, poleLapMs)}</td>
		`;
		tbody.appendChild(tr);
	});
}

function renderPoleDisplay(element, qualifyingResults, fallbackText) {
	if (!element) return;
	element.textContent = qualifyingResults.length
		? `Pole: ${qualifyingResults[0].driver_name} (${formatLapTime(qualifyingResults[0].best_lap_ms)})`
		: fallbackText;
}

function resetRacePlaybackDisplay(elements) {
	if (elements.commentaryLog) elements.commentaryLog.innerHTML = '';
	if (elements.lapCounter) elements.lapCounter.textContent = '0 / 0';
	if (elements.leaderDisplay) elements.leaderDisplay.textContent = '-';
	if (elements.fastestLapDisplay) elements.fastestLapDisplay.textContent = '-';
	if (elements.latestCommentary) elements.latestCommentary.textContent = 'Awaiting lights out.';
	if (elements.pauseBtn) {
		elements.pauseBtn.textContent = 'Pause';
		elements.pauseBtn.disabled = false;
	}
}

function setRaceScreenVisibility(elements, { showWeekend, showStrategy, showResults }) {
	if (elements.weekendPanel) elements.weekendPanel.style.display = showWeekend ? 'grid' : 'none';
	if (elements.strategyPanel) elements.strategyPanel.style.display = showStrategy ? 'grid' : 'none';
	if (elements.resultsContainer) elements.resultsContainer.style.display = showResults ? 'block' : 'none';
}

function formatQualifyingGap(bestLapMs, poleLapMs) {
	if (!Number.isFinite(bestLapMs) || !Number.isFinite(poleLapMs)) return '-';
	if (bestLapMs === poleLapMs) return 'POLE';
	return `+${((bestLapMs - poleLapMs) / 1000).toFixed(3)}s`;
}

function buildCommentaryLine(event) {
	if (!event) return null;
	if (event.type === 'position_change') {
		return `Lap ${event.lap}: ${event.driver_name} moves up to P${event.to_position}.`;
	}
	if (event.type === 'lead_change') {
		return `Lap ${event.lap}: ${event.driver_name} takes the lead.`;
	}
	if (event.type === 'turn_one_leader') {
		return `Lap ${event.lap}: ${event.driver_name} leads out of turn 1.`;
	}
	if (event.type === 'turn_one_pushed_wide') {
		return `Lap ${event.lap}: ${event.driver_name} is pushed wide at turn 1 and drops ${event.positions_lost} place(s).`;
	}
	if (event.type === 'turn_one_checked_up') {
		return `Lap ${event.lap}: ${event.driver_name} is checked up at turn 1 and loses ${event.positions_lost} place(s).`;
	}
	if (event.type === 'turn_one_spin') {
		return `Lap ${event.lap}: ${event.driver_name} spins at turn 1 and falls back ${event.positions_lost} place(s).`;
	}
	if (event.type === 'turn_one_crash') {
		return `Lap ${event.lap}: ${event.driver_name} crashes out at turn 1.`;
	}
	if (event.type === 'pit_stop') {
		return `Lap ${event.lap}: ${event.driver_name} pits for fuel, stop ${event.stop_number}.`;
	}
	if (event.type === 'fastest_lap') {
		return `Lap ${event.lap}: ${event.driver_name} sets the fastest lap at ${formatLapTime(event.lap_time_ms)}.`;
	}
	if (event.type === 'retirement') {
		return `Lap ${event.lap}: ${event.driver_name} retires with a ${event.reason}.`;
	}
	return null;
}

function buildPitStopCounts(lapHistory, lapNumber) {
	const counts = new Map();
	for (const lap of lapHistory.slice(0, lapNumber)) {
		if (!Array.isArray(lap.events)) continue;
		for (const event of lap.events) {
			if (event.type !== 'pit_stop') continue;
			counts.set(event.driver_id, (counts.get(event.driver_id) || 0) + 1);
		}
	}
	return counts;
}

function stopRaceAutoplay() {
	if (raceAutoplayTimer) {
		window.clearInterval(raceAutoplayTimer);
		raceAutoplayTimer = null;
	}
	raceAutoplayData = null;
	raceAutoplayLapIndex = 0;
	raceAutoplayPaused = false;
	const pauseBtn = document.getElementById('race-pause-btn');
	if (pauseBtn) {
		pauseBtn.textContent = 'Pause';
		pauseBtn.disabled = false;
	}
}

export function setRacePlaybackCompleteHandler(handler) {
	onRacePlaybackComplete = typeof handler === 'function' ? handler : null;
}

function activateRaceTab(tabName = 'timing') {
	const tabButtons = document.querySelectorAll('.race-tab-btn');
	const timingPanel = document.getElementById('race-panel-timing');
	const qualifyingPanel = document.getElementById('race-panel-qualifying');
	const commentaryPanel = document.getElementById('race-panel-commentary');
	const chartPanel = document.getElementById('race-panel-chart');
	const laptimesPanel = document.getElementById('race-panel-laptimes');

	tabButtons.forEach((button) => {
		button.classList.toggle('active', button.dataset.raceTab === tabName);
	});
	if (timingPanel) timingPanel.style.display = tabName === 'timing' ? '' : 'none';
	if (qualifyingPanel) qualifyingPanel.style.display = tabName === 'qualifying' ? '' : 'none';
	if (commentaryPanel) commentaryPanel.style.display = tabName === 'commentary' ? '' : 'none';
	if (chartPanel) chartPanel.style.display = tabName === 'chart' ? '' : 'none';
	if (laptimesPanel) laptimesPanel.style.display = tabName === 'laptimes' ? '' : 'none';
}

export function enterRaceView(nextEventEl, weekEl) {
	stopRaceAutoplay();
	currentRaceWeekendData = null;
	const elements = getRaceElements();
	const event = nextEventEl.textContent;
	if (elements.raceName) elements.raceName.textContent = event.replace('Next: ', '').split(' - ')[0] || 'Grand Prix';
	if (elements.raceWeek) elements.raceWeek.textContent = weekEl.textContent;
	if (elements.circuitDisplay) elements.circuitDisplay.textContent = 'Loading weekend data...';
	if (elements.locationDisplay) elements.locationDisplay.textContent = '-';
	if (elements.lapsDisplay) elements.lapsDisplay.textContent = '-';
	renderPoleDisplay(elements.poleDisplay, [], 'No grid set yet.');
	setRaceStatus(
		elements.statusText,
		elements.statusChip,
		'Qualifying must be completed before the race can begin.',
		'Qualifying Pending',
		'pending',
	);
	if (elements.qualifyingBody) {
		elements.qualifyingBody.innerHTML = '<tr class="race-qualifying-placeholder"><td colspan="4">Loading race weekend...</td></tr>';
	}
	if (elements.qualifyingBtn) {
		elements.qualifyingBtn.disabled = true;
		elements.qualifyingBtn.textContent = 'RUN QUALIFYING';
	}
	if (elements.simBtn) {
		elements.simBtn.disabled = true;
		elements.simBtn.textContent = 'SIMULATE RACE';
		elements.simBtn.style.display = '';
	}
	setRaceScreenVisibility(elements, { showWeekend: true, showStrategy: false, showResults: false });
	resetRacePlaybackDisplay(elements);
	activateRaceTab('timing');

	if (elements.raceView) elements.raceView.style.display = 'flex';
}

export function renderRaceWeekend(data = currentRaceWeekendData) {
	if (!data) return;
	stopRaceAutoplay();
	currentRaceWeekendData = data;
	const elements = getRaceElements();
	const qualifyingResults = Array.isArray(data.qualifying_results) ? data.qualifying_results : [];
	const qualifyingComplete = !!data.qualifying_complete;
	const raceComplete = !!data.race_complete;

	if (elements.circuitDisplay) elements.circuitDisplay.textContent = data.circuit_name || data.event_name || 'Grand Prix';
	if (elements.locationDisplay) elements.locationDisplay.textContent = [data.circuit_location, data.circuit_country].filter(Boolean).join(', ') || '-';
	if (elements.lapsDisplay) elements.lapsDisplay.textContent = Number.isFinite(data.laps) ? `${data.laps} laps` : '-';
	renderQualifyingTable(elements.qualifyingBody, qualifyingResults, 'Run qualifying to set the grid.');
	renderPoleDisplay(elements.poleDisplay, qualifyingResults, 'No grid set yet.');

	if (raceComplete) {
		setRaceStatus(
			elements.statusText,
			elements.statusChip,
			'The race has already been run. Replay data is shown below.',
			'Race Complete',
			'complete',
		);
	} else if (qualifyingComplete) {
		setRaceStatus(elements.statusText, elements.statusChip, 'Grid locked in. The race is ready to simulate.', 'Grid Set', 'ready');
	} else {
		setRaceStatus(
			elements.statusText,
			elements.statusChip,
			'Qualifying must be completed before the race can begin.',
			'Qualifying Pending',
			'pending',
		);
	}

	if (elements.qualifyingBtn) {
		elements.qualifyingBtn.disabled = qualifyingComplete || raceComplete;
		elements.qualifyingBtn.textContent = qualifyingComplete ? 'QUALIFYING COMPLETE' : 'RUN QUALIFYING';
	}
	if (elements.simBtn) {
		elements.simBtn.disabled = !qualifyingComplete || raceComplete;
		elements.simBtn.textContent = raceComplete ? 'RACE COMPLETE' : 'SIMULATE RACE';
		elements.simBtn.style.display = '';
	}
	setRaceScreenVisibility(elements, {
		showWeekend: true,
		showStrategy: false,
		showResults: raceComplete,
	});
}

function strategyCardMarkup(strategy) {
	const plannedPitLaps = Array.isArray(strategy.planned_pit_laps) ? strategy.planned_pit_laps : [];
	return `
		<div class="race-strategy-card" data-driver-id="${strategy.driver_id}">
			<div class="race-strategy-card-head">
				<div>
					<h3>${strategy.driver_name}</h3>
					<p>${strategy.grid_position ? `Grid: P${strategy.grid_position}` : 'Grid: TBD'}</p>
				</div>
				<div class="race-strategy-stop-block">
					<label for="race-strategy-stops-${strategy.driver_id}">Stops</label>
					<select id="race-strategy-stops-${strategy.driver_id}" class="race-strategy-stop-select" data-driver-id="${strategy.driver_id}">
						<option value="1"${strategy.planned_stops === 1 ? ' selected' : ''}>1 stop</option>
						<option value="2"${strategy.planned_stops === 2 ? ' selected' : ''}>2 stops</option>
						<option value="3"${strategy.planned_stops === 3 ? ' selected' : ''}>3 stops</option>
					</select>
				</div>
			</div>
			<div class="race-strategy-plan">
				<span class="race-summary-label">Planned Laps</span>
				<strong>${plannedPitLaps.map((lap) => `Lap ${lap}`).join(', ') || 'No stops planned'}</strong>
			</div>
			<button class="btn-secondary race-strategy-regenerate-btn" data-driver-id="${strategy.driver_id}">Regenerate</button>
		</div>
	`;
}

export function renderRaceStrategyScreen(data = currentRaceWeekendData) {
	if (!data) return;
	currentRaceWeekendData = data;
	const elements = getRaceElements();
	const strategies = Array.isArray(data.player_strategies) ? data.player_strategies : [];

	if (elements.eventDisplay) elements.eventDisplay.textContent = data.event_name || data.circuit_name || 'Grand Prix';
	if (elements.strategyCards) {
		elements.strategyCards.innerHTML = strategies.map(strategyCardMarkup).join('');
		if (!strategies.length) {
			elements.strategyCards.innerHTML = '<div class="placeholder-msg">No player cars are available for strategy setup.</div>';
		}
	}
	if (elements.strategyStartBtn) {
		elements.strategyStartBtn.disabled = !data.qualifying_complete || data.race_complete || !strategies.length;
		elements.strategyStartBtn.textContent = 'START RACE';
	}
	setRaceScreenVisibility(elements, { showWeekend: false, showStrategy: true, showResults: false });
}

export function openRaceStrategyScreen() {
	renderRaceStrategyScreen(currentRaceWeekendData);
}

export function collectRaceStrategySelections() {
	return Array.from(document.querySelectorAll('.race-strategy-stop-select')).map((select) => ({
		driver_id: Number(select.dataset.driverId),
		planned_stops: Number(select.value),
	}));
}

function renderLapSnapshot(data, lapIndex) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	if (!lapHistory.length) return;

	const snapshot = lapHistory[Math.max(0, Math.min(lapIndex, lapHistory.length - 1))];
	const timingRows = Array.isArray(snapshot.order) ? snapshot.order : [];
	const pitStopCounts = buildPitStopCounts(lapHistory, snapshot.lap);
	const elements = getRaceElements();

	elements.timingBody.innerHTML = '';
	timingRows.forEach((row) => {
		const statusLabel = row.status === 'DNF' ? 'DNF' : (row.status || 'RUNNING');
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${row.position}</td>
			<td>${row.driver_name}</td>
			<td>${row.team_name}</td>
			<td>${pitStopCounts.get(row.driver_id) || 0}</td>
			<td>${formatLapTime(row.last_lap_ms)}</td>
			<td>${formatLapTime(row.best_lap_ms)}</td>
			<td>${row.gap_display || '-'}</td>
			<td>${statusLabel}</td>
		`;
		elements.timingBody.appendChild(tr);
	});

	const leader = timingRows[0];
	if (elements.lapCounter) elements.lapCounter.textContent = `${snapshot.lap} / ${data.total_laps || lapHistory.length}`;
	if (elements.leaderDisplay) elements.leaderDisplay.textContent = leader ? `${leader.driver_name} (${leader.team_name})` : '-';

	let fastestEvent = null;
	for (const lap of lapHistory) {
		if (!Array.isArray(lap.events)) continue;
		for (const event of lap.events) {
			if (event.type === 'fastest_lap') fastestEvent = event;
		}
	}
	if (elements.fastestLapDisplay) {
		elements.fastestLapDisplay.textContent = fastestEvent
			? `${fastestEvent.driver_name} ${formatLapTime(fastestEvent.lap_time_ms)}`
			: '-';
	}

	if (elements.commentaryLog) {
		const lines = [];
		let previousLeaderId = null;
		for (const lap of lapHistory.slice(0, snapshot.lap)) {
			const currentLeader = Array.isArray(lap.order) ? lap.order[0] : null;
			if (currentLeader && previousLeaderId !== null && currentLeader.driver_id !== previousLeaderId) {
				const line = buildCommentaryLine({
					type: 'lead_change',
					lap: lap.lap,
					driver_name: currentLeader.driver_name,
				});
				if (line) lines.push(line);
			}
			(Array.isArray(lap.events) ? lap.events : []).forEach((event) => {
				const line = buildCommentaryLine(event);
				if (line) lines.push(line);
			});
			if (currentLeader) previousLeaderId = currentLeader.driver_id;
		}
		elements.commentaryLog.innerHTML = '';
		lines.forEach((line) => {
			const item = document.createElement('div');
			item.className = 'race-commentary-item';
			item.textContent = line;
			elements.commentaryLog.appendChild(item);
		});
		if (elements.latestCommentary) elements.latestCommentary.textContent = lines.at(-1) || 'Awaiting the next flashpoint.';
	}

	if (elements.prevBtn) elements.prevBtn.disabled = snapshot.lap <= 1;
	if (elements.nextBtn) elements.nextBtn.disabled = snapshot.lap >= lapHistory.length;
	if (elements.resultsContainer) {
		elements.resultsContainer.dataset.activeLapIndex = String(Math.max(0, Math.min(lapIndex, lapHistory.length - 1)));
	}
}

function startRaceAutoplay(data) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	const elements = getRaceElements();
	if (!lapHistory.length || !elements.resultsContainer) return;

	stopRaceAutoplay();
	raceAutoplayData = data;
	raceAutoplayLapIndex = 0;
	raceAutoplayPaused = false;
	renderLapSnapshot(data, raceAutoplayLapIndex);

	const tickRaceAutoplay = () => {
		if (!raceAutoplayData) return;
		raceAutoplayLapIndex += 1;
		if (raceAutoplayLapIndex >= lapHistory.length) {
			renderLapSnapshot(data, lapHistory.length - 1);
			if (elements.pauseBtn) elements.pauseBtn.disabled = true;
			const completionHandler = onRacePlaybackComplete;
			onRacePlaybackComplete = null;
			stopRaceAutoplay();
			if (completionHandler) completionHandler();
			return;
		}
		renderLapSnapshot(data, raceAutoplayLapIndex);
	};

	if (elements.pauseBtn) {
		elements.pauseBtn.textContent = 'Pause';
		elements.pauseBtn.disabled = false;
		elements.pauseBtn.onclick = () => {
			if (!raceAutoplayData) return;
			if (raceAutoplayPaused) {
				raceAutoplayPaused = false;
				elements.pauseBtn.textContent = 'Pause';
				raceAutoplayTimer = window.setInterval(tickRaceAutoplay, RACE_AUTOPLAY_INTERVAL_MS);
				return;
			}
			raceAutoplayPaused = true;
			elements.pauseBtn.textContent = 'Resume';
			if (raceAutoplayTimer) {
				window.clearInterval(raceAutoplayTimer);
				raceAutoplayTimer = null;
			}
		};
	}

	raceAutoplayTimer = window.setInterval(tickRaceAutoplay, RACE_AUTOPLAY_INTERVAL_MS);
}

export function renderRaceResults(data) {
	currentRaceWeekendData = data;
	const elements = getRaceElements();
	const qualifyingResults = Array.isArray(data.qualifying_results) ? data.qualifying_results : [];

	renderQualifyingTable(elements.qualifyingResultsBody, qualifyingResults, 'No qualifying data recorded.');
	renderPoleDisplay(elements.qualifyingPoleDisplay, qualifyingResults, '-');

	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	if (!lapHistory.length) {
		stopRaceAutoplay();
		if (elements.pauseBtn) elements.pauseBtn.disabled = true;
		elements.timingBody.innerHTML = '';
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
				<td>-</td>
				<td>-</td>
				<td>-</td>
				<td>-</td>
				<td>${statusLabel}</td>
			`;
			elements.timingBody.appendChild(row);
		});
	} else {
		renderLapChart(data);
		renderLaptimeChart(data);
		if (elements.timingTab) elements.timingTab.onclick = () => activateRaceTab('timing');
		if (elements.qualifyingTab) elements.qualifyingTab.onclick = () => activateRaceTab('qualifying');
		if (elements.commentaryTab) elements.commentaryTab.onclick = () => activateRaceTab('commentary');
		if (elements.chartTab) elements.chartTab.onclick = () => activateRaceTab('chart');
		if (elements.laptimesTab) elements.laptimesTab.onclick = () => activateRaceTab('laptimes');
		if (elements.prevBtn) {
			elements.prevBtn.onclick = () => {
				if (raceAutoplayTimer) {
					window.clearInterval(raceAutoplayTimer);
					raceAutoplayTimer = null;
				}
				raceAutoplayPaused = true;
				if (elements.pauseBtn) elements.pauseBtn.textContent = 'Resume';
				const current = Number(elements.resultsContainer.dataset.activeLapIndex || (lapHistory.length - 1));
				const nextIndex = Math.max(0, current - 1);
				raceAutoplayLapIndex = nextIndex;
				renderLapSnapshot(data, nextIndex);
			};
		}
		if (elements.nextBtn) {
			elements.nextBtn.onclick = () => {
				if (raceAutoplayTimer) {
					window.clearInterval(raceAutoplayTimer);
					raceAutoplayTimer = null;
				}
				raceAutoplayPaused = true;
				if (elements.pauseBtn) elements.pauseBtn.textContent = 'Resume';
				const current = Number(elements.resultsContainer.dataset.activeLapIndex || (lapHistory.length - 1));
				const nextIndex = Math.min(lapHistory.length - 1, current + 1);
				raceAutoplayLapIndex = nextIndex;
				renderLapSnapshot(data, nextIndex);
			};
		}
		startRaceAutoplay(data);
	}

	setRaceScreenVisibility(elements, { showWeekend: false, showStrategy: false, showResults: true });
	if (elements.simBtn) elements.simBtn.style.display = 'none';
	activateRaceTab('timing');
}

export function exitRaceView() {
	stopRaceAutoplay();
	currentRaceWeekendData = null;
	const { raceView } = getRaceElements();
	if (raceView) raceView.style.display = 'none';

	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn) {
		advanceBtn.textContent = 'ADVANCE';
		advanceBtn.classList.remove('event-active');
	}
}
