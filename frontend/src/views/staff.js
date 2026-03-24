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
		this.workforceEditor = document.getElementById('staff-workforce-editor');
		this.workforceInput = document.getElementById('staff-workforce-input');
		this.workforceApplyBtn = document.getElementById('staff-workforce-apply-btn');
		this.workforcePayroll = document.getElementById('staff-workforce-payroll');
		this.workforceTableBody = document.getElementById('staff-workforce-table-body');
		this.onReplaceDriver = null;
		this.onReplaceCommercialManager = null;
		this.onReplaceTechnicalDirector = null;
		this.onUpdateWorkforce = null;
		this.bindTabs();
		this.bindWorkforceEditor();
	}

	setReplaceDriverHandler(handler) {
		this.onReplaceDriver = handler;
	}

	setReplaceCommercialManagerHandler(handler) {
		this.onReplaceCommercialManager = handler;
	}

	setReplaceTechnicalDirectorHandler(handler) {
		this.onReplaceTechnicalDirector = handler;
	}

	setUpdateWorkforceHandler(handler) {
		this.onUpdateWorkforce = handler;
	}

	bindWorkforceEditor() {
		if (!this.workforceApplyBtn || !this.workforceInput) return;
		this.workforceApplyBtn.addEventListener('click', () => {
			if (!this.onUpdateWorkforce) return;
			const value = Number(this.workforceInput.value);
			if (!Number.isFinite(value)) return;
			this.onUpdateWorkforce(value);
		});
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
		const maxAllowed = Number(data?.workforce_limits?.max) || 250;
		const maxWorkforce = teams.length > 0 ? Math.max(...teams.map((t) => Number(t.workforce) || 0)) : 1;
		const perRacePayroll = Number(data?.projected_workforce_race_cost) || 0;
		const annualPayroll = Number(data?.projected_workforce_annual_cost) || 0;
		const racesInSeason = Number(data?.races_in_season) || 0;

		this.workforceSummary.textContent = `${playerTeamName} workforce: ${playerWorkforce.toLocaleString()} staff`;
		if (this.workforceInput) {
			this.workforceInput.value = String(playerWorkforce);
			this.workforceInput.max = String(maxAllowed);
		}
		if (this.workforcePayroll) {
			this.workforcePayroll.textContent = `Projected payroll: $${perRacePayroll.toLocaleString()} per race (${racesInSeason} races), $${annualPayroll.toLocaleString()} per year`;
		}
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
		const cm = data?.commercial_manager;
		if (!td && !cm) {
			this.managementContainer.innerHTML = '<p style="color: #64748b;">No management staff assigned.</p>';
			return;
		}

		const renderCard = (member, roleLabel, showCountry = false, replaceType = null) => {
			if (!member) return '';
			const portraitFile = encodeURIComponent((member.name || '').toLowerCase() + '.png');
			const absSalary = Math.abs(member.salary || 0);
			const salaryFormatted = '$' + absSalary.toLocaleString();
			const isReplaceable = replaceType === 'technical_director' || replaceType === 'commercial_manager';
			const buttonClass = replaceType === 'technical_director'
				? 'staff-replace-technical-director-btn'
				: 'staff-replace-manager-btn';
			const dataAttr = replaceType === 'technical_director'
				? `data-director-id="${member.id}"`
				: `data-manager-id="${member.id}"`;
			return `
				<div class="staff-driver-card">
					<div class="staff-card-role">${roleLabel}</div>
					<div class="staff-card-portrait">
						<img src="assets/managers/${portraitFile}" alt="${member.name}" onerror="this.style.display='none'">
					</div>
					<h3 class="staff-card-name">${member.name}</h3>
					<div class="staff-card-details">
						${showCountry ? `
						<div class="staff-detail-row">
							<span class="staff-detail-label">Country</span>
							<span class="staff-detail-value">${renderFlagLabel(member.country || '', member.country || 'Unknown')}</span>
						</div>` : ''}
						<div class="staff-detail-row">
							<span class="staff-detail-label">Age</span>
							<span class="staff-detail-value">${member.age}</span>
						</div>
						<div class="staff-detail-row">
							<span class="staff-detail-label">Skill</span>
							<span class="staff-detail-value">${this.renderSkillBlocks(member.skill)}</span>
						</div>
						<div class="staff-detail-row">
							<span class="staff-detail-label">Contract</span>
							<span class="staff-detail-value">${member.contract_length} year(s)</span>
						</div>
						<div class="staff-detail-row">
							<span class="staff-detail-label">Salary</span>
							<span class="staff-detail-value">${salaryFormatted}</span>
						</div>
						${isReplaceable ? `
						<div class="staff-detail-row">
							<span class="staff-detail-value">
								<button class="staff-replace-btn ${buttonClass}" ${dataAttr} ${member.contract_length >= 2 || member.pending_replacement ? 'disabled' : ''}>
									Replace
								</button>
							</span>
						</div>` : ''}
					</div>
				</div>
			`;
		};

		this.managementContainer.innerHTML = `
			${renderCard(td, 'Technical Director', true, 'technical_director')}
			${renderCard(cm, 'Commercial Manager', true, 'commercial_manager')}
		`;

		this.managementContainer.querySelectorAll('.staff-replace-technical-director-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onReplaceTechnicalDirector) return;
				const directorId = Number(btn.getAttribute('data-director-id'));
				if (!Number.isFinite(directorId)) return;
				this.onReplaceTechnicalDirector(directorId);
			});
		});

		this.managementContainer.querySelectorAll('.staff-replace-manager-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onReplaceCommercialManager) return;
				const managerId = Number(btn.getAttribute('data-manager-id'));
				if (!Number.isFinite(managerId)) return;
				this.onReplaceCommercialManager(managerId);
			});
		});
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
					<div class="staff-detail-row">
						<span class="staff-detail-label">Contract</span>
						<span class="staff-detail-value">${driver.contract_length} year(s)</span>
					</div>
					<div class="staff-detail-row">
						<span class="staff-detail-value">
							<button class="staff-replace-btn" data-driver-id="${driver.id}" ${driver.contract_length >= 2 || driver.pending_replacement ? 'disabled' : ''}>
								Replace
							</button>
						</span>
					</div>
				</div>
			`;

			this.container.appendChild(card);
		});

		this.container.querySelectorAll('.staff-replace-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onReplaceDriver) return;
				const driverId = Number(btn.getAttribute('data-driver-id'));
				if (!Number.isFinite(driverId)) return;
				this.onReplaceDriver(driverId);
			});
		});

		if (drivers.length === 0) {
			this.container.innerHTML = '<p style="color: #64748b;">No drivers assigned.</p>';
		}

		this.renderWorkforce(data);
		this.renderManagement(data);
	}
}
