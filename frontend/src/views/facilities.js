/**
 * Facilities View
 * Displays the player's team factory/facilities rating.
 */

export default class FacilitiesView {
	constructor() {
		this.container = document.getElementById('facilities-container');
	}

	render(data) {
		this.container.innerHTML = '';

		const rating = data.facilities || 0;
		const teamName = data.team_name || 'Unknown';

		// Determine tier label and color
		let tier, tierColor;
		if (rating >= 80) {
			tier = 'World Class';
			tierColor = '#22c55e';
		} else if (rating >= 60) {
			tier = 'Competitive';
			tierColor = '#3b82f6';
		} else if (rating >= 40) {
			tier = 'Midfield';
			tierColor = '#f59e0b';
		} else {
			tier = 'Underdeveloped';
			tierColor = '#ef4444';
		}

		this.container.innerHTML = `
			<div class="facilities-card">
				<div class="facilities-header">
					<h3 class="facilities-team-name">${teamName} Factory</h3>
					<span class="facilities-tier" style="color: ${tierColor}">${tier}</span>
				</div>
				<div class="facilities-rating-display">
					<span class="facilities-rating-number" style="color: ${tierColor}">${rating}</span>
					<span class="facilities-rating-max">/ 100</span>
				</div>
				<div class="facilities-bar-bg">
					<div class="facilities-bar-fill" style="width: ${rating}%; background: ${tierColor}"></div>
				</div>
			</div>
		`;
	}
}
