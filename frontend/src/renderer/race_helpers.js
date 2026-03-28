import { formatLapTime, renderLapChart, renderLaptimeChart } from './race_charts.js';

const RACE_AUTOPLAY_INTERVAL_MS = 450;
let raceAutoplayTimer = null;
let raceAutoplayData = null;
let raceAutoplayLapIndex = 0;
let raceAutoplayPaused = false;

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
	const raceView = document.getElementById('race-view');
	const event = nextEventEl.textContent;
	const raceName = document.getElementById('race-event-name');
	const raceWeek = document.getElementById('race-week-display');
	const qualifyingBtn = document.getElementById('simulate-qualifying-btn');
	const simBtn = document.getElementById('simulate-race-btn');
	const qualifyingBody = document.getElementById('race-qualifying-body');
	const circuitDisplay = document.getElementById('race-circuit-display');
	const locationDisplay = document.getElementById('race-location-display');
	const lapsDisplay = document.getElementById('race-laps-display');
	const poleDisplay = document.getElementById('race-pole-display');
	const statusText = document.getElementById('race-weekend-status');
	const statusChip = document.getElementById('race-status-chip');
	const weekendPanel = document.getElementById('race-weekend-panel');

	raceName.textContent = event.replace('Next: ', '').split(' - ')[0] || 'Grand Prix';
	raceWeek.textContent = weekEl.textContent;
	if (circuitDisplay) circuitDisplay.textContent = 'Loading weekend data...';
	if (locationDisplay) locationDisplay.textContent = '-';
	if (lapsDisplay) lapsDisplay.textContent = '-';
	if (poleDisplay) poleDisplay.textContent = 'No grid set yet.';
	if (statusText) statusText.textContent = 'Qualifying must be completed before the race can begin.';
	if (statusChip) {
		statusChip.textContent = 'Qualifying Pending';
		statusChip.className = 'race-status-chip pending';
	}
	if (qualifyingBody) {
		qualifyingBody.innerHTML = '<tr class="race-qualifying-placeholder"><td colspan="4">Loading race weekend...</td></tr>';
	}
	if (qualifyingBtn) {
		qualifyingBtn.disabled = true;
		qualifyingBtn.textContent = 'RUN QUALIFYING';
	}
	if (simBtn) {
		simBtn.disabled = true;
		simBtn.textContent = 'SIMULATE RACE';
		simBtn.style.display = '';
	}
	if (weekendPanel) weekendPanel.style.display = 'grid';
	document.getElementById('race-results-container').style.display = 'none';
	const commentaryLog = document.getElementById('race-commentary-log');
	const lapCounter = document.getElementById('race-lap-counter');
	const leaderDisplay = document.getElementById('race-leader-display');
	const fastestLapDisplay = document.getElementById('race-fastest-lap-display');
	const latestCommentary = document.getElementById('race-latest-commentary');
	const pauseBtn = document.getElementById('race-pause-btn');
	if (commentaryLog) commentaryLog.innerHTML = '';
	if (lapCounter) lapCounter.textContent = '0 / 0';
	if (leaderDisplay) leaderDisplay.textContent = '-';
	if (fastestLapDisplay) fastestLapDisplay.textContent = '-';
	if (latestCommentary) latestCommentary.textContent = 'Awaiting lights out.';
	if (pauseBtn) {
		pauseBtn.textContent = 'Pause';
		pauseBtn.disabled = false;
	}
	activateRaceTab('timing');

	raceView.style.display = 'flex';
}

export function renderRaceWeekend(data) {
	stopRaceAutoplay();
	const qualifyingBtn = document.getElementById('simulate-qualifying-btn');
	const simBtn = document.getElementById('simulate-race-btn');
	const qualifyingBody = document.getElementById('race-qualifying-body');
	const circuitDisplay = document.getElementById('race-circuit-display');
	const locationDisplay = document.getElementById('race-location-display');
	const lapsDisplay = document.getElementById('race-laps-display');
	const poleDisplay = document.getElementById('race-pole-display');
	const statusText = document.getElementById('race-weekend-status');
	const statusChip = document.getElementById('race-status-chip');
	const weekendPanel = document.getElementById('race-weekend-panel');
	const resultsContainer = document.getElementById('race-results-container');
	const qualifyingResults = Array.isArray(data.qualifying_results) ? data.qualifying_results : [];
	const qualifyingComplete = !!data.qualifying_complete;
	const raceComplete = !!data.race_complete;

	if (circuitDisplay) circuitDisplay.textContent = data.circuit_name || data.event_name || 'Grand Prix';
	if (locationDisplay) locationDisplay.textContent = [data.circuit_location, data.circuit_country].filter(Boolean).join(', ') || '-';
	if (lapsDisplay) lapsDisplay.textContent = Number.isFinite(data.laps) ? `${data.laps} laps` : '-';
	if (qualifyingBody) {
		qualifyingBody.innerHTML = '';
		if (!qualifyingResults.length) {
			qualifyingBody.innerHTML = '<tr class="race-qualifying-placeholder"><td colspan="5">Run qualifying to set the grid.</td></tr>';
		} else {
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
				qualifyingBody.appendChild(tr);
			});
		}
	}

	if (poleDisplay) {
		poleDisplay.textContent = qualifyingResults.length
			? `Pole: ${qualifyingResults[0].driver_name} (${formatLapTime(qualifyingResults[0].best_lap_ms)})`
			: 'No grid set yet.';
	}

	if (raceComplete) {
		if (statusText) statusText.textContent = 'The race has already been run. Replay data is shown below.';
		if (statusChip) {
			statusChip.textContent = 'Race Complete';
			statusChip.className = 'race-status-chip complete';
		}
	} else if (qualifyingComplete) {
		if (statusText) statusText.textContent = 'Grid locked in. The race is ready to simulate.';
		if (statusChip) {
			statusChip.textContent = 'Grid Set';
			statusChip.className = 'race-status-chip ready';
		}
	} else {
		if (statusText) statusText.textContent = 'Qualifying must be completed before the race can begin.';
		if (statusChip) {
			statusChip.textContent = 'Qualifying Pending';
			statusChip.className = 'race-status-chip pending';
		}
	}

	if (qualifyingBtn) {
		qualifyingBtn.disabled = qualifyingComplete || raceComplete;
		qualifyingBtn.textContent = qualifyingComplete ? 'QUALIFYING COMPLETE' : 'RUN QUALIFYING';
	}
	if (simBtn) {
		simBtn.disabled = !qualifyingComplete || raceComplete;
		simBtn.textContent = raceComplete ? 'RACE COMPLETE' : 'SIMULATE RACE';
		simBtn.style.display = '';
	}
	if (weekendPanel) weekendPanel.style.display = 'grid';
	if (resultsContainer && !raceComplete) resultsContainer.style.display = 'none';
}

function renderLapSnapshot(data, lapIndex) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	if (!lapHistory.length) return;

	const snapshot = lapHistory[Math.max(0, Math.min(lapIndex, lapHistory.length - 1))];
	const timingRows = Array.isArray(snapshot.order) ? snapshot.order : [];
	const pitStopCounts = buildPitStopCounts(lapHistory, snapshot.lap);
	const tbody = document.getElementById('race-results-body');
	const lapCounter = document.getElementById('race-lap-counter');
	const leaderDisplay = document.getElementById('race-leader-display');
	const fastestLapDisplay = document.getElementById('race-fastest-lap-display');
	const commentaryLog = document.getElementById('race-commentary-log');
	const latestCommentary = document.getElementById('race-latest-commentary');
	const prevBtn = document.getElementById('race-prev-lap-btn');
	const nextBtn = document.getElementById('race-next-lap-btn');
	const resultsContainer = document.getElementById('race-results-container');

	tbody.innerHTML = '';
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
		tbody.appendChild(tr);
	});

	const leader = timingRows[0];
	if (lapCounter) lapCounter.textContent = `${snapshot.lap} / ${data.total_laps || lapHistory.length}`;
	if (leaderDisplay) leaderDisplay.textContent = leader ? `${leader.driver_name} (${leader.team_name})` : '-';

	let fastestEvent = null;
	for (const lap of lapHistory) {
		if (!Array.isArray(lap.events)) continue;
		for (const event of lap.events) {
			if (event.type === 'fastest_lap') fastestEvent = event;
		}
	}
	if (fastestLapDisplay) {
		fastestLapDisplay.textContent = fastestEvent
			? `${fastestEvent.driver_name} ${formatLapTime(fastestEvent.lap_time_ms)}`
			: '-';
	}

	if (commentaryLog) {
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
		commentaryLog.innerHTML = '';
		lines.forEach((line) => {
			const item = document.createElement('div');
			item.className = 'race-commentary-item';
			item.textContent = line;
			commentaryLog.appendChild(item);
		});
		if (latestCommentary) latestCommentary.textContent = lines.at(-1) || 'Awaiting the next flashpoint.';
	}

	if (prevBtn) prevBtn.disabled = snapshot.lap <= 1;
	if (nextBtn) nextBtn.disabled = snapshot.lap >= lapHistory.length;
	if (resultsContainer) resultsContainer.dataset.activeLapIndex = String(Math.max(0, Math.min(lapIndex, lapHistory.length - 1)));
}

function startRaceAutoplay(data) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	const resultsContainer = document.getElementById('race-results-container');
	const pauseBtn = document.getElementById('race-pause-btn');
	if (!lapHistory.length || !resultsContainer) return;

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
			if (pauseBtn) pauseBtn.disabled = true;
			stopRaceAutoplay();
			return;
		}
		renderLapSnapshot(data, raceAutoplayLapIndex);
	};

	if (pauseBtn) {
		pauseBtn.textContent = 'Pause';
		pauseBtn.disabled = false;
		pauseBtn.onclick = () => {
			if (!raceAutoplayData) return;
			if (raceAutoplayPaused) {
				raceAutoplayPaused = false;
				pauseBtn.textContent = 'Pause';
				raceAutoplayTimer = window.setInterval(tickRaceAutoplay, RACE_AUTOPLAY_INTERVAL_MS);
				return;
			}
			raceAutoplayPaused = true;
			pauseBtn.textContent = 'Resume';
			if (raceAutoplayTimer) {
				window.clearInterval(raceAutoplayTimer);
				raceAutoplayTimer = null;
			}
		};
	}

	raceAutoplayTimer = window.setInterval(tickRaceAutoplay, RACE_AUTOPLAY_INTERVAL_MS);
}

export function renderRaceResults(data) {
	const tbody = document.getElementById('race-results-body');
	const container = document.getElementById('race-results-container');
	const weekendPanel = document.getElementById('race-weekend-panel');
	const qualifyingResultsBody = document.getElementById('race-results-qualifying-body');
	const qualifyingPoleDisplay = document.getElementById('race-results-pole-display');
	const simulateBtn = document.getElementById('simulate-race-btn');
	const prevBtn = document.getElementById('race-prev-lap-btn');
	const nextBtn = document.getElementById('race-next-lap-btn');
	const pauseBtn = document.getElementById('race-pause-btn');
	const timingTab = document.getElementById('race-tab-timing');
	const qualifyingTab = document.getElementById('race-tab-qualifying');
	const commentaryTab = document.getElementById('race-tab-commentary');
	const chartTab = document.getElementById('race-tab-chart');
	const laptimesTab = document.getElementById('race-tab-laptimes');
	const qualifyingResults = Array.isArray(data.qualifying_results) ? data.qualifying_results : [];

	if (qualifyingResultsBody) {
		qualifyingResultsBody.innerHTML = '';
		if (!qualifyingResults.length) {
			qualifyingResultsBody.innerHTML = '<tr class="race-qualifying-placeholder"><td colspan="5">No qualifying data recorded.</td></tr>';
		} else {
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
				qualifyingResultsBody.appendChild(tr);
			});
		}
	}
	if (qualifyingPoleDisplay) {
		qualifyingPoleDisplay.textContent = qualifyingResults.length
			? `Pole: ${qualifyingResults[0].driver_name} (${formatLapTime(qualifyingResults[0].best_lap_ms)})`
			: '-';
	}

	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	if (!lapHistory.length) {
		stopRaceAutoplay();
		if (pauseBtn) pauseBtn.disabled = true;
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
				<td>-</td>
				<td>-</td>
				<td>-</td>
				<td>-</td>
				<td>${statusLabel}</td>
			`;
			tbody.appendChild(row);
		});
	} else {
		renderLapChart(data);
		renderLaptimeChart(data);
		if (timingTab) timingTab.onclick = () => activateRaceTab('timing');
		if (qualifyingTab) qualifyingTab.onclick = () => activateRaceTab('qualifying');
		if (commentaryTab) commentaryTab.onclick = () => activateRaceTab('commentary');
		if (chartTab) chartTab.onclick = () => activateRaceTab('chart');
		if (laptimesTab) laptimesTab.onclick = () => activateRaceTab('laptimes');
		if (prevBtn) {
			prevBtn.onclick = () => {
				if (raceAutoplayTimer) {
					window.clearInterval(raceAutoplayTimer);
					raceAutoplayTimer = null;
				}
				raceAutoplayPaused = true;
				if (pauseBtn) pauseBtn.textContent = 'Resume';
				const current = Number(container.dataset.activeLapIndex || (lapHistory.length - 1));
				const nextIndex = Math.max(0, current - 1);
				raceAutoplayLapIndex = nextIndex;
				renderLapSnapshot(data, nextIndex);
			};
		}
		if (nextBtn) {
			nextBtn.onclick = () => {
				if (raceAutoplayTimer) {
					window.clearInterval(raceAutoplayTimer);
					raceAutoplayTimer = null;
				}
				raceAutoplayPaused = true;
				if (pauseBtn) pauseBtn.textContent = 'Resume';
				const current = Number(container.dataset.activeLapIndex || (lapHistory.length - 1));
				const nextIndex = Math.min(lapHistory.length - 1, current + 1);
				raceAutoplayLapIndex = nextIndex;
				renderLapSnapshot(data, nextIndex);
			};
		}
		startRaceAutoplay(data);
	}

	if (weekendPanel) weekendPanel.style.display = 'none';
	simulateBtn.style.display = 'none';
	container.style.display = 'block';
	activateRaceTab('timing');
}

export function exitRaceView() {
	stopRaceAutoplay();
	const raceView = document.getElementById('race-view');
	raceView.style.display = 'none';

	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn) {
		advanceBtn.textContent = 'ADVANCE';
		advanceBtn.classList.remove('event-active');
	}
}
