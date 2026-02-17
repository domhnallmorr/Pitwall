/**
 * Staff View Module
 * Displays the player's two drivers in side-by-side cards.
 */
import { renderFlagLabel } from './flags.js';

export default class StaffView {
	constructor() {
		this.container = document.getElementById('staff-drivers-container');
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
			blocks += `<span class="staff-speed-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="staff-speed-rating" role="img" aria-label="Speed rating ${rating} out of 5">${blocks}</span>`;
	}

	render(data) {
		this.container.innerHTML = '';

		const drivers = data.drivers || [];

		drivers.forEach((driver, index) => {
			const card = document.createElement('div');
			card.className = 'staff-driver-card';

			const roleLabel = index === 0 ? 'Driver 1' : 'Driver 2';
			const portraitFile = driver.name.toLowerCase() + '.png';

			// Format wage
			const absWage = Math.abs(driver.wage);
			const wageFormatted = '$' + absWage.toLocaleString();
			const wageDisplay = driver.pay_driver
				? `<span class="staff-pay-driver">${wageFormatted} (Pay Driver)</span>`
				: wageFormatted;

			card.innerHTML = `
				<div class="staff-card-role">${roleLabel}</div>
				<div class="staff-card-portrait">
					<img src="assets/drivers/${portraitFile}" alt="${driver.name}" onerror="this.style.display='none'">
				</div>
				<h3 class="staff-card-name">${driver.name}</h3>
				<div class="staff-card-details">
					<div class="staff-detail-row">
						<span class="staff-detail-label">Age</span>
						<span class="staff-detail-value">${driver.age}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Country</span>
						<span class="staff-detail-value">${renderFlagLabel(driver.country, driver.country)}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Speed</span>
						<span class="staff-detail-value">${this.renderSpeedBlocks(driver.speed)}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Wage</span>
						<span class="staff-detail-value">${wageDisplay}</span>
					</div>
				</div>
			`;

			this.container.appendChild(card);
		});

		if (drivers.length === 0) {
			this.container.innerHTML = '<p style="color: #64748b;">No drivers assigned.</p>';
		}
	}
}
