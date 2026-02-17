/**
 * Driver View Module
 * Shows a dedicated profile card for one driver.
 */
import { renderFlagLabel } from './flags.js';

export default class DriverView {
	constructor() {
		this.container = document.getElementById('driver-profile-container');
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

	render(data) {
		if (!this.container) return;
		this.currentDriverName = data?.name || null;
		if (this.title) this.title.textContent = data?.name || 'Driver Profile';

		if (!data || !data.name) {
			this.container.innerHTML = '<p style="color: #64748b;">Driver not found.</p>';
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
	}
}
