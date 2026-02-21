/**
 * Car View Module
 * Displays team car speed comparison.
 */
export default class CarView {
	constructor() {
		this.body = document.getElementById('car-table-body');
	}

	getSpeedRating(speed) {
		const numericSpeed = Number(speed);
		const clamped = Number.isFinite(numericSpeed) ? Math.max(0, Math.min(100, numericSpeed)) : 0;
		return Math.max(1, Math.ceil(clamped / 20));
	}

	renderRatingBlocks(value, label) {
		const rating = this.getSpeedRating(value);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="car-speed-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="car-speed-rating" role="img" aria-label="${label} rating ${rating} out of 5">${blocks}</span>`;
	}

	render(data) {
		if (!this.body) return;
		const teams = (data?.teams || []).slice().sort((a, b) => (b.car_speed ?? 0) - (a.car_speed ?? 0));

		this.body.innerHTML = '';
		teams.forEach((team, index) => {
			const row = document.createElement('tr');
			row.innerHTML = `
				<td>${index + 1}</td>
				<td>${team.name}</td>
				<td>${team.country || '-'}</td>
				<td>${this.renderRatingBlocks(team.car_speed, 'Car speed')}</td>
				<td>${this.renderRatingBlocks(team.engine_power || 0, 'Engine power')}</td>
			`;
			this.body.appendChild(row);
		});
	}
}
