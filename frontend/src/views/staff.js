/**
 * Staff View Module
 * Displays the player's two drivers in side-by-side cards.
 */
import { renderFlagLabel } from './flags.js';

export default class StaffView {
	constructor() {
		this.container = document.getElementById('staff-drivers-container');
		this.tabBtns = document.querySelectorAll('.staff-tab-btn');
		this.driversContent = document.getElementById('staff-content-drivers');
		this.workforceContent = document.getElementById('staff-content-workforce');
		this.managementContent = document.getElementById('staff-content-management');
		this.managementContainer = document.getElementById('staff-management-container');
		this.workforceSummary = document.getElementById('staff-workforce-summary');
		this.workforceTableBody = document.getElementById('staff-workforce-table-body');
		this.bindTabs();
	}

	bindTabs() {
		if (!this.tabBtns.length) return;
		this.tabBtns.forEach((btn) => {
			btn.addEventListener('click', () => {
				this.tabBtns.forEach((b) => b.classList.remove('active'));
				btn.classList.add('active');
				const type = btn.getAttribute('data-type');
				if (type === 'workforce') {
					if (this.driversContent) this.driversContent.style.display = 'none';
					if (this.workforceContent) this.workforceContent.style.display = 'block';
					if (this.managementContent) this.managementContent.style.display = 'none';
				} else if (type === 'management') {
					if (this.driversContent) this.driversContent.style.display = 'none';
					if (this.workforceContent) this.workforceContent.style.display = 'none';
					if (this.managementContent) this.managementContent.style.display = 'block';
				} else {
					if (this.driversContent) this.driversContent.style.display = 'block';
					if (this.workforceContent) this.workforceContent.style.display = 'none';
					if (this.managementContent) this.managementContent.style.display = 'none';
				}
			});
		});
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

	renderSkillBlocks(skill) {
		const rating = this.getSpeedRating(skill);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="staff-skill-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="staff-skill-rating" role="img" aria-label="Skill rating ${rating} out of 5">${blocks}</span>`;
	}

	getWorkforceRating(workforce, maxWorkforce) {
		const value = Number(workforce) || 0;
		const max = Math.max(1, Number(maxWorkforce) || 1);
		return Math.max(1, Math.ceil((value / max) * 5));
	}

	renderWorkforceBlocks(workforce, maxWorkforce) {
		const rating = this.getWorkforceRating(workforce, maxWorkforce);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="staff-workforce-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="staff-workforce-rating" role="img" aria-label="Workforce rating ${rating} out of 5">${blocks}</span>`;
	}

	renderWorkforce(data) {
		if (!this.workforceTableBody || !this.workforceSummary) return;
		const teams = (data?.teams || []).slice().sort((a, b) => (b.workforce ?? 0) - (a.workforce ?? 0));
		const playerTeamName = data?.team_name || 'Your team';
		const playerWorkforce = Number(data?.player_workforce) || 0;
		const maxWorkforce = teams.length > 0 ? Math.max(...teams.map((t) => Number(t.workforce) || 0)) : 1;

		this.workforceSummary.textContent = `${playerTeamName} workforce: ${playerWorkforce.toLocaleString()} staff`;
		this.workforceTableBody.innerHTML = '';

		teams.forEach((team, index) => {
			const row = document.createElement('tr');
			row.innerHTML = `
				<td>${index + 1}</td>
				<td>${team.name}</td>
				<td>${team.country || '-'}</td>
				<td>${this.renderWorkforceBlocks(team.workforce, maxWorkforce)}</td>
			`;
			this.workforceTableBody.appendChild(row);
		});
	}

	renderManagement(data) {
		if (!this.managementContainer) return;
		const td = data?.technical_director;
		if (!td) {
			this.managementContainer.innerHTML = '<p style="color: #64748b;">No technical director assigned.</p>';
			return;
		}

		const portraitFile = encodeURIComponent((td.name || '').toLowerCase() + '.png');
		const absSalary = Math.abs(td.salary || 0);
		const salaryFormatted = '$' + absSalary.toLocaleString();

		this.managementContainer.innerHTML = `
			<div class="staff-driver-card">
				<div class="staff-card-role">Technical Director</div>
				<div class="staff-card-portrait">
					<img src="assets/managers/${portraitFile}" alt="${td.name}" onerror="this.style.display='none'">
				</div>
				<h3 class="staff-card-name">${td.name}</h3>
				<div class="staff-card-details">
					<div class="staff-detail-row">
						<span class="staff-detail-label">Country</span>
						<span class="staff-detail-value">${renderFlagLabel(td.country || '', td.country || 'Unknown')}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Age</span>
						<span class="staff-detail-value">${td.age}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Skill</span>
						<span class="staff-detail-value">${this.renderSkillBlocks(td.skill)}</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Contract</span>
						<span class="staff-detail-value">${td.contract_length} year(s)</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-label">Salary</span>
						<span class="staff-detail-value">${salaryFormatted}</span>
					</div>
				</div>
			</div>
		`;
	}

	render(data) {
		if (!this.container) return;
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

		this.renderWorkforce(data);
		this.renderManagement(data);
	}
}
