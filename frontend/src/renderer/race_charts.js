export function formatLapTime(ms) {
	if (!Number.isFinite(ms) || ms <= 0) return '-';
	return (ms / 1000).toFixed(3) + 's';
}

export function renderLapChart(data) {
	const lapHistory = Array.isArray(data.lap_history) ? data.lap_history : [];
	const svg = document.getElementById('race-lap-chart-svg');
	const legend = document.getElementById('race-lap-chart-legend');
	if (!svg || !legend) return;

	svg.innerHTML = '';
	legend.innerHTML = '';
	if (!lapHistory.length) return;

	const colors = ['#64ffda', '#ffcc66', '#ff7a59', '#7cb7ff', '#d29bff', '#91f27a', '#ff8fb1', '#f4f1de'];
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
			.map((position, index) => (position ? `${xForLap(index)},${yForPosition(position)}` : null))
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

export function renderLaptimeChart(data) {
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
