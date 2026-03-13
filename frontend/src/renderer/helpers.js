export function updateBalance(balanceEl, amount) {
	const formatted = '$' + Math.abs(amount).toLocaleString();
	balanceEl.textContent = amount < 0 ? '-' + formatted : formatted;
	balanceEl.className = amount < 0 ? 'balance-info balance-negative' : 'balance-info';
}

const RACE_AUTOPLAY_INTERVAL_MS = 450;
let raceAutoplayTimer = null;
let raceAutoplayData = null;
let raceAutoplayLapIndex = 0;
let raceAutoplayPaused = false;

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
	const commentaryPanel = document.getElementById('race-panel-commentary');
	const chartPanel = document.getElementById('race-panel-chart');
	const laptimesPanel = document.getElementById('race-panel-laptimes');

	tabButtons.forEach((button) => {
		button.classList.toggle('active', button.dataset.raceTab === tabName);
	});
	if (timingPanel) timingPanel.style.display = tabName === 'timing' ? '' : 'none';
	if (commentaryPanel) commentaryPanel.style.display = tabName === 'commentary' ? '' : 'none';
	if (chartPanel) chartPanel.style.display = tabName === 'chart' ? '' : 'none';
	if (laptimesPanel) laptimesPanel.style.display = tabName === 'laptimes' ? '' : 'none';
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
	stopRaceAutoplay();
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

function formatLapTime(ms) {
	if (!Number.isFinite(ms) || ms <= 0) return '-';
	return (ms / 1000).toFixed(3) + 's';
}

function buildCommentaryLine(event, timingRows) {
	if (!event) return null;
	if (event.type === 'position_change') {
		return `Lap ${event.lap}: ${event.driver_name} moves up to P${event.to_position}.`;
	}
	if (event.type === 'lead_change') {
		return `Lap ${event.lap}: ${event.driver_name} takes the lead.`;
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

function renderLapChart(data) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	const svg = document.getElementById('race-lap-chart-svg');
	const legend = document.getElementById('race-lap-chart-legend');
	if (!svg || !legend) return;

	svg.innerHTML = '';
	legend.innerHTML = '';
	if (!lapHistory.length) return;

	const colors = [
		'#64ffda',
		'#ffcc66',
		'#ff7a59',
		'#7cb7ff',
		'#d29bff',
		'#91f27a',
		'#ff8fb1',
		'#f4f1de',
	];
	const width = 900;
	const height = 520;
	const padding = { top: 30, right: 30, bottom: 44, left: 52 };
	const plotWidth = width - padding.left - padding.right;
	const plotHeight = height - padding.top - padding.bottom;
	const maxPosition = Math.max(...lapHistory.flatMap((lap) => (lap.order || []).map((row) => row.position || 0)), 1);
	const lapCount = lapHistory.length;

	const driverMap = new Map();
	lapHistory.forEach((lap) => {
		(lap.order || []).forEach((row) => {
			if (!driverMap.has(row.driver_id)) {
				driverMap.set(row.driver_id, {
					driver_name: row.driver_name,
					team_name: row.team_name,
					positions: [],
					color: colors[driverMap.size % colors.length],
				});
			}
		});
	});

	lapHistory.forEach((lap, lapIndex) => {
		(lap.order || []).forEach((row) => {
			driverMap.get(row.driver_id).positions[lapIndex] = row.position;
		});
	});

	svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

	const makeSvg = (tag, attrs = {}) => {
		const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
		Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
		return element;
	};
	const shouldDrawLapMarker = (lapNumber) => lapNumber === 1 || lapNumber === lapCount || lapNumber % 5 === 0;
	const xForLap = (lapIndex) => padding.left + (lapCount === 1 ? plotWidth / 2 : (lapIndex / (lapCount - 1)) * plotWidth);
	const yForPosition = (position) => padding.top + ((position - 1) / Math.max(1, maxPosition - 1 || 1)) * plotHeight;

	for (let gridPosition = 1; gridPosition <= maxPosition; gridPosition += 1) {
		const y = yForPosition(gridPosition);
		svg.appendChild(makeSvg('line', {
			x1: padding.left,
			y1: y,
			x2: width - padding.right,
			y2: y,
			stroke: 'rgba(136, 146, 176, 0.18)',
			'stroke-width': 1,
		}));
		const label = makeSvg('text', {
			x: padding.left - 12,
			y: y + 4,
			'text-anchor': 'end',
			fill: '#8892b0',
			'font-size': 12,
		});
		label.textContent = `P${gridPosition}`;
		svg.appendChild(label);
	}

	lapHistory.forEach((lap, lapIndex) => {
		if (!shouldDrawLapMarker(lap.lap)) return;
		const x = xForLap(lapIndex);
		svg.appendChild(makeSvg('line', {
			x1: x,
			y1: padding.top,
			x2: x,
			y2: height - padding.bottom,
			stroke: 'rgba(136, 146, 176, 0.12)',
			'stroke-width': 1,
		}));
		const label = makeSvg('text', {
			x,
			y: height - 16,
			'text-anchor': 'middle',
			fill: '#8892b0',
			'font-size': 12,
		});
		label.textContent = `L${lap.lap}`;
		svg.appendChild(label);
	});

	Array.from(driverMap.values()).forEach((driver) => {
		const points = driver.positions
			.map((position, index) => {
				if (!position) return null;
				return `${xForLap(index)},${yForPosition(position)}`;
			})
			.filter(Boolean);
		if (!points.length) return;

		svg.appendChild(makeSvg('polyline', {
			points: points.join(' '),
			fill: 'none',
			stroke: driver.color,
			'stroke-width': 3,
			'stroke-linejoin': 'round',
			'stroke-linecap': 'round',
			class: 'race-lap-chart-line',
		}));

		driver.positions.forEach((position, index) => {
			if (!position) return;
			svg.appendChild(makeSvg('circle', {
				cx: xForLap(index),
				cy: yForPosition(position),
				r: 4,
				fill: driver.color,
				class: 'race-lap-chart-point',
			}));
		});

		const legendItem = document.createElement('div');
		legendItem.className = 'race-lap-chart-legend-item';
		legendItem.innerHTML = `
			<span class="race-lap-chart-legend-swatch" style="background:${driver.color}"></span>
			<span>${driver.driver_name}</span>
		`;
		legend.appendChild(legendItem);
	});
}

function renderLaptimeChart(data) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	const svg = document.getElementById('race-laptime-svg');
	const legend = document.getElementById('race-laptime-legend');
	const selectors = [
		document.getElementById('race-laptime-driver-1'),
		document.getElementById('race-laptime-driver-2'),
		document.getElementById('race-laptime-driver-3'),
		document.getElementById('race-laptime-driver-4'),
	].filter(Boolean);
	if (!svg || !legend || !selectors.length) return;

	svg.innerHTML = '';
	legend.innerHTML = '';
	if (!lapHistory.length) return;

	const colors = ['#64ffda', '#ffcc66', '#ff7a59', '#7cb7ff'];
	const width = 900;
	const height = 520;
	const padding = { top: 30, right: 30, bottom: 44, left: 58 };
	const plotWidth = width - padding.left - padding.right;
	const plotHeight = height - padding.top - padding.bottom;
	const lapCount = lapHistory.length;

	const driverMap = new Map();
	const pitStopEventsByDriver = new Map();
	lapHistory.forEach((lap) => {
		(lap.order || []).forEach((row) => {
			if (!driverMap.has(row.driver_id)) {
				driverMap.set(row.driver_id, {
					driver_id: row.driver_id,
					driver_name: row.driver_name,
					team_name: row.team_name,
					lapTimes: [],
				});
			}
		});
		(lap.events || []).forEach((event) => {
			if (event.type !== 'pit_stop') return;
			if (!pitStopEventsByDriver.has(event.driver_id)) {
				pitStopEventsByDriver.set(event.driver_id, []);
			}
			pitStopEventsByDriver.get(event.driver_id).push(lap.lap);
		});
	});
	lapHistory.forEach((lap, lapIndex) => {
		(lap.order || []).forEach((row) => {
			driverMap.get(row.driver_id).lapTimes[lapIndex] = row.last_lap_ms ?? null;
		});
	});
	const pitStopLapsByDriver = new Map();
	driverMap.forEach((driver, driverId) => {
		const eventLaps = pitStopEventsByDriver.get(driverId) || [];
		const mappedPitLaps = new Set();
		eventLaps.forEach((eventLap) => {
			const currentLapTime = driver.lapTimes[eventLap - 1];
			const nextLapTime = driver.lapTimes[eventLap];
			if (Number.isFinite(nextLapTime) && (!Number.isFinite(currentLapTime) || nextLapTime > currentLapTime)) {
				mappedPitLaps.add(eventLap + 1);
				return;
			}
			mappedPitLaps.add(eventLap);
		});
		pitStopLapsByDriver.set(driverId, mappedPitLaps);
	});

	const drivers = Array.from(driverMap.values());
	const defaultIds = drivers.slice(0, 4).map((driver) => String(driver.driver_id));
	selectors.forEach((select, index) => {
		const currentValue = select.value || defaultIds[index] || '';
		select.innerHTML = '<option value="">Select driver</option>';
		drivers.forEach((driver) => {
			const option = document.createElement('option');
			option.value = String(driver.driver_id);
			option.textContent = driver.driver_name;
			select.appendChild(option);
		});
		if (drivers.some((driver) => String(driver.driver_id) === currentValue)) {
			select.value = currentValue;
		} else {
			select.value = defaultIds[index] || '';
		}
	});

	const selectedDrivers = selectors
		.map((select, index) => {
			const driver = driverMap.get(Number(select.value));
			if (!driver) return null;
			return {
				...driver,
				color: colors[index % colors.length],
				pitLaps: pitStopLapsByDriver.get(driver.driver_id) || new Set(),
			};
		})
		.filter(Boolean);

	const allLapTimes = selectedDrivers.flatMap((driver) => driver.lapTimes.filter((lapTime, index) => (
		Number.isFinite(lapTime) && !driver.pitLaps.has(index + 1)
	)));
	if (!allLapTimes.length) return;
	const minLapTime = Math.min(...allLapTimes);
	const maxLapTime = Math.max(...allLapTimes);
	const rangeLapTime = Math.max(1, maxLapTime - minLapTime);

	svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
	const makeSvg = (tag, attrs = {}) => {
		const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
		Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
		return element;
	};
	const shouldDrawLapMarker = (lapNumber) => lapNumber === 1 || lapNumber === lapCount || lapNumber % 5 === 0;
	const xForLap = (lapIndex) => padding.left + (lapCount === 1 ? plotWidth / 2 : (lapIndex / (lapCount - 1)) * plotWidth);
	const yForLapTime = (lapTime) => padding.top + ((lapTime - minLapTime) / rangeLapTime) * plotHeight;
	const boundedYForLapTime = (lapTime) => Math.max(padding.top, Math.min(height - padding.bottom, yForLapTime(lapTime)));

	for (let marker = 0; marker < 5; marker += 1) {
		const lapTime = minLapTime + ((maxLapTime - minLapTime) * marker) / 4;
		const y = yForLapTime(lapTime);
		svg.appendChild(makeSvg('line', {
			x1: padding.left,
			y1: y,
			x2: width - padding.right,
			y2: y,
			stroke: 'rgba(136, 146, 176, 0.18)',
			'stroke-width': 1,
		}));
		const label = makeSvg('text', {
			x: padding.left - 14,
			y: y + 4,
			'text-anchor': 'end',
			fill: '#8892b0',
			'font-size': 12,
		});
		label.textContent = formatLapTime(lapTime);
		svg.appendChild(label);
	}

	lapHistory.forEach((lap, lapIndex) => {
		if (!shouldDrawLapMarker(lap.lap)) return;
		const x = xForLap(lapIndex);
		svg.appendChild(makeSvg('line', {
			x1: x,
			y1: padding.top,
			x2: x,
			y2: height - padding.bottom,
			stroke: 'rgba(136, 146, 176, 0.12)',
			'stroke-width': 1,
		}));
		const label = makeSvg('text', {
			x,
			y: height - 16,
			'text-anchor': 'middle',
			fill: '#8892b0',
			'font-size': 12,
		});
		label.textContent = `L${lap.lap}`;
		svg.appendChild(label);
	});

	selectedDrivers.forEach((driver) => {
		const segments = [];
		let currentSegment = [];
		driver.lapTimes.forEach((lapTime, index) => {
			const lapNumber = index + 1;
			if (!Number.isFinite(lapTime) || driver.pitLaps.has(lapNumber)) {
				if (currentSegment.length) {
					segments.push(currentSegment);
					currentSegment = [];
				}
				return;
			}
			currentSegment.push(`${xForLap(index)},${boundedYForLapTime(lapTime)}`);
		});
		if (currentSegment.length) {
			segments.push(currentSegment);
		}

		segments.forEach((segment) => {
			if (segment.length < 1) return;
			svg.appendChild(makeSvg('polyline', {
				points: segment.join(' '),
				fill: 'none',
				stroke: driver.color,
				'stroke-width': 3,
				'stroke-linejoin': 'round',
				'stroke-linecap': 'round',
				class: 'race-lap-chart-line',
			}));
		});

		driver.lapTimes.forEach((lapTime, index) => {
			if (!Number.isFinite(lapTime)) return;
			const lapNumber = index + 1;
			const cx = xForLap(index);
			const cy = boundedYForLapTime(lapTime);
			if (driver.pitLaps.has(lapNumber)) {
				svg.appendChild(makeSvg('rect', {
					x: cx - 5,
					y: cy - 5,
					width: 10,
					height: 10,
					rx: 2,
					fill: driver.color,
					class: 'race-laptime-pit-marker',
				}));
				return;
			}
			svg.appendChild(makeSvg('circle', {
				cx,
				cy,
				r: 4,
				fill: driver.color,
				class: 'race-lap-chart-point',
			}));
		});

		const legendItem = document.createElement('div');
		legendItem.className = 'race-lap-chart-legend-item';
		legendItem.innerHTML = `
			<span class="race-lap-chart-legend-swatch" style="background:${driver.color}"></span>
			<span>${driver.driver_name}${driver.pitLaps.size ? ' (square = pit lap)' : ''}</span>
		`;
		legend.appendChild(legendItem);
	});

	selectors.forEach((select) => {
		select.onchange = () => renderLaptimeChart(data);
	});
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
	if (fastestLapDisplay) fastestLapDisplay.textContent = fastestEvent
		? `${fastestEvent.driver_name} ${formatLapTime(fastestEvent.lap_time_ms)}`
		: '-';

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
				}, lap.order);
				if (line) lines.push(line);
			}
			(Array.isArray(lap.events) ? lap.events : []).forEach((event) => {
				const line = buildCommentaryLine(event, lap.order);
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

	raceAutoplayTimer = window.setInterval(tickRaceAutoplay, RACE_AUTOPLAY_INTERVAL_MS);
}

export function renderRaceResults(data) {
	const tbody = document.getElementById('race-results-body');
	const container = document.getElementById('race-results-container');
	const simulateBtn = document.getElementById('simulate-race-btn');
	const prevBtn = document.getElementById('race-prev-lap-btn');
	const nextBtn = document.getElementById('race-next-lap-btn');
	const pauseBtn = document.getElementById('race-pause-btn');
	const timingTab = document.getElementById('race-tab-timing');
	const commentaryTab = document.getElementById('race-tab-commentary');
	const chartTab = document.getElementById('race-tab-chart');
	const laptimesTab = document.getElementById('race-tab-laptimes');

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
		if (commentaryTab) commentaryTab.onclick = () => activateRaceTab('commentary');
		if (chartTab) chartTab.onclick = () => activateRaceTab('chart');
		if (laptimesTab) laptimesTab.onclick = () => activateRaceTab('laptimes');
		if (prevBtn) prevBtn.onclick = () => {
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
		if (nextBtn) nextBtn.onclick = () => {
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
		startRaceAutoplay(data);
	}

	simulateBtn.style.display = 'none';
	container.style.display = 'block';
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
