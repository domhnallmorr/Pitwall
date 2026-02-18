/**
 * Driver View Module
 * Shows a dedicated profile card for one driver.
 */
import { renderFlagLabel } from './flags.js';
import { toFlagSlug } from './flags.js';

export default class DriverView {
	constructor() {
		this.container = document.getElementById('driver-profile-container');
		this.seasonContainer = document.getElementById('driver-season-results-container');
		this.title = document.getElementById('driver-profile-title');
		this.currentDriverName = null;
	}

	getSpeedRating(speed) {
		const numericSpeed = Number(speed);
		const clamped = Number.isFinite(numericSpeed) ? Math.max(0, Math.min(100, numericSpeed)) : 0;
		return Math.max(1, Math.ceil(clamped / 20));
	}

	renderSpeedBlocks(speed) {
		const rating = this.getSpeedRating(speed);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="driver-speed-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="driver-speed-rating" role="img" aria-label="Speed rating ${rating} out of 5">${blocks}</span>`;
	}

	renderSeasonResults(results) {
		const rows = Array.isArray(results) ? results : [];
		if (rows.length === 0) {
			return '<div class="driver-season-empty">No race results recorded this season yet.</div>';
		}

		const flagCells = rows.map((r) => {
			const country = r.country || 'Unknown';
			const flagSlug = toFlagSlug(country);
			const primarySrc = `assets/flags/${encodeURIComponent(country)}.png`;
			const fallbackSrc = `assets/flags/${flagSlug}.png`;
			return `
				<td class="driver-season-flag-cell" title="Round ${r.round}: ${country}">
					<img class="app-flag" src="${primarySrc}" alt="${country} flag" onerror="if(!this.dataset.fallback){this.dataset.fallback='1';this.src='${fallbackSrc}';}else{this.style.display='none';}">
				</td>
			`;
		}).join('');

		const posCells = rows.map((r) => {
			const pos = Number(r.position) || 0;
			const podiumClass = pos === 1 ? 'is-gold' : pos === 2 ? 'is-silver' : pos === 3 ? 'is-bronze' : '';
			return `<td class="driver-season-pos-cell ${podiumClass}">${pos}</td>`;
		}).join('');

		return `
			<div class="driver-season-results">
				<div class="driver-season-title">Season Results</div>
				<table class="driver-season-table">
					<tbody>
						<tr>${flagCells}</tr>
						<tr>${posCells}</tr>
					</tbody>
				</table>
			</div>
		`;
	}

	render(data) {
		if (!this.container) return;
		this.currentDriverName = data?.name || null;
		if (this.title) this.title.textContent = data?.name || 'Driver Profile';

		if (!data || !data.name) {
			this.container.innerHTML = '<p style="color: #64748b;">Driver not found.</p>';
			if (this.seasonContainer) this.seasonContainer.innerHTML = '';
			return;
		}

		const absWage = Math.abs(data.wage || 0);
		const wageFormatted = '$' + absWage.toLocaleString();
		const wageDisplay = data.pay_driver
			? `<span class="staff-pay-driver">${wageFormatted} (Pay Driver)</span>`
			: wageFormatted;

		const portraitFile = data.name.toLowerCase() + '.png';

		this.container.innerHTML = `
			<div class="staff-driver-card driver-profile-card">
				<div class="staff-card-portrait">
					<img src="assets/drivers/${portraitFile}" alt="${data.name}" onerror="this.style.display='none'">
				</div>
				<h3 class="staff-card-name">${data.name}</h3>
				<div class="staff-card-details">
					<div class="staff-detail-row">
						<span class="staff-detail-label">Team</span>
						<span class="staff-detail-value">${data.team_name || 'Free Agent'}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Age</span>
						<span class="staff-detail-value">${data.age}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Country</span>
						<span class="staff-detail-value">${renderFlagLabel(data.country, data.country)}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Speed</span>
						<span class="staff-detail-value">${this.renderSpeedBlocks(data.speed)}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Race Starts</span>
						<span class="staff-detail-value">${(data.race_starts || 0).toLocaleString()}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Wins</span>
						<span class="staff-detail-value">${(data.wins || 0).toLocaleString()}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Points</span>
						<span class="staff-detail-value">${data.points || 0}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Wage</span>
						<span class="staff-detail-value">${wageDisplay}</span>
					</div>
				</div>
			</div>
		`;
		if (this.seasonContainer) {
			this.seasonContainer.innerHTML = this.renderSeasonResults(data.season_results);
		}
	}
}
