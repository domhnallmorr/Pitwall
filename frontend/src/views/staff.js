/**
 * Staff View Module
 * Displays the player's two drivers in side-by-side cards.
 */

export default class StaffView {
	constructor() {
		this.container = document.getElementById('staff-drivers-container');
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
						<span class="staff-detail-value">${driver.country}</span>
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
