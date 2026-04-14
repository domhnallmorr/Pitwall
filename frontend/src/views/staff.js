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
		this.operationalContent = document.getElementById('staff-content-operational');
		this.managementContent = document.getElementById('staff-content-management');
		this.commercialContent = document.getElementById('staff-content-commercial');
		this.managementContainer = document.getElementById('staff-management-container');
		this.operationalSummary = document.getElementById('staff-operational-summary');
		this.operationalPayroll = document.getElementById('staff-operational-payroll');
		this.operationalTableBody = document.getElementById('staff-operational-table-body');
		this.commercialSummary = document.getElementById('staff-commercial-summary');
		this.commercialPayroll = document.getElementById('staff-commercial-payroll');
		this.commercialTableBody = document.getElementById('staff-commercial-table-body');
		this.onSelectDriver = null;
		this.onReplaceDriver = null;
		this.onReplaceCommercialManager = null;
		this.onReplaceTechnicalDirector = null;
		this.activeOperationalTab = 'design';
		this.lastRenderData = null;
		this.bindTabs();
	}

	setReplaceDriverHandler(handler) {
		this.onReplaceDriver = handler;
	}

	setDriverSelectHandler(handler) {
		this.onSelectDriver = handler;
	}

	setReplaceCommercialManagerHandler(handler) {
		this.onReplaceCommercialManager = handler;
	}

	setReplaceTechnicalDirectorHandler(handler) {
		this.onReplaceTechnicalDirector = handler;
	}

	bindTabs() {
		if (!this.tabBtns.length) return;
		this.tabBtns.forEach((btn) => {
			btn.addEventListener('click', () => {
				this.tabBtns.forEach((b) => b.classList.remove('active'));
				btn.classList.add('active');
				const type = btn.getAttribute('data-type');
				if (type === 'design' || type === 'engineering' || type === 'mechanics') {
					this.activeOperationalTab = type;
					if (this.driversContent) this.driversContent.style.display = 'none';
					if (this.operationalContent) this.operationalContent.style.display = 'block';
					if (this.managementContent) this.managementContent.style.display = 'none';
					if (this.commercialContent) this.commercialContent.style.display = 'none';
					this.renderOperationalDepartment(this.lastRenderData, type);
				} else if (type === 'commercial') {
					if (this.driversContent) this.driversContent.style.display = 'none';
					if (this.operationalContent) this.operationalContent.style.display = 'none';
					if (this.managementContent) this.managementContent.style.display = 'none';
					if (this.commercialContent) this.commercialContent.style.display = 'block';
				} else if (type === 'management') {
					if (this.driversContent) this.driversContent.style.display = 'none';
					if (this.operationalContent) this.operationalContent.style.display = 'none';
					if (this.managementContent) this.managementContent.style.display = 'block';
					if (this.commercialContent) this.commercialContent.style.display = 'none';
				} else {
					if (this.driversContent) this.driversContent.style.display = 'block';
					if (this.operationalContent) this.operationalContent.style.display = 'none';
					if (this.managementContent) this.managementContent.style.display = 'none';
					if (this.commercialContent) this.commercialContent.style.display = 'none';
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

	renderOperationalDepartment(data, departmentKey = this.activeOperationalTab) {
		if (!this.operationalTableBody || !this.operationalSummary) return;
		const playerTeamName = data?.team_name || 'Your team';
		const playerWorkforce = Number(data?.player_workforce) || 0;
		const maxAllowed = Number(data?.workforce_limits?.max) || 250;
		const factorySize = Number(data?.factory_size) || 1;
		const racesInSeason = Number(data?.races_in_season) || 0;
		const operational = data?.operational_staff || {};
		const definitions = {
			design: {
				label: 'Design',
				count: Number(operational.design_count) || 0,
				annualWage: Number(operational.design_annual_avg_wage) || 0,
			},
			engineering: {
				label: 'Engineering',
				count: Number(operational.engineering_count) || 0,
				annualWage: Number(operational.engineering_annual_avg_wage) || 0,
			},
			mechanics: {
				label: 'Mechanics',
				count: Number(operational.mechanics_count) || 0,
				annualWage: Number(operational.mechanics_annual_avg_wage) || 0,
			},
		};
		const department = definitions[departmentKey] || definitions.design;
		const annualPayroll = department.count * department.annualWage;
		const racePayroll = racesInSeason > 0 ? Math.round(annualPayroll / racesInSeason) : annualPayroll;

		this.operationalSummary.textContent = `${playerTeamName} ${department.label.toLowerCase()} staff: ${department.count.toLocaleString()} staff (Factory ${factorySize} star, operational cap ${maxAllowed.toLocaleString()}, total operational staff ${playerWorkforce.toLocaleString()})`;
		if (this.operationalPayroll) {
			this.operationalPayroll.textContent = `Projected payroll: $${racePayroll.toLocaleString()} per race (${racesInSeason} races), $${annualPayroll.toLocaleString()} per year`;
		}
		this.operationalTableBody.innerHTML = `
			<tr>
				<td>Average</td>
				<td>${department.count.toLocaleString()}</td>
				<td>$${department.annualWage.toLocaleString()}</td>
				<td>$${annualPayroll.toLocaleString()}</td>
				<td>$${racePayroll.toLocaleString()}</td>
			</tr>
		`;
	}

	renderCommercial(data) {
		if (!this.commercialTableBody || !this.commercialSummary) return;
		const teamName = data?.team_name || 'Your team';
		const staffCount = Number(data?.player_commercial_staff) || 0;
		const maxAllowed = Number(data?.commercial_staff_limits?.max) || staffCount;
		const factorySize = Number(data?.factory_size) || 1;
		const annualWage = Number(data?.commercial_staff_annual_avg_wage) || 0;
		const racePayroll = Number(data?.projected_commercial_staff_race_cost) || 0;
		const annualPayroll = Number(data?.projected_commercial_staff_annual_cost) || 0;
		const racesInSeason = Number(data?.races_in_season) || 0;

		this.commercialSummary.textContent = `${teamName} commercial staff: ${staffCount.toLocaleString()} / ${maxAllowed.toLocaleString()} staff (Factory ${factorySize} star)`;
		if (this.commercialPayroll) {
			this.commercialPayroll.textContent = `Projected payroll: $${racePayroll.toLocaleString()} per race (${racesInSeason} races), $${annualPayroll.toLocaleString()} per year`;
		}
		this.commercialTableBody.innerHTML = `
			<tr>
				<td>Average</td>
				<td>${staffCount.toLocaleString()}</td>
				<td>$${annualWage.toLocaleString()}</td>
				<td>$${annualPayroll.toLocaleString()}</td>
				<td>$${racePayroll.toLocaleString()}</td>
			</tr>
		`;
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
		this.lastRenderData = data;
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
				<h3 class="staff-card-name"><button type="button" class="driver-link staff-driver-link" data-driver-name="${driver.name}">${driver.name}</button></h3>
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

		this.container.querySelectorAll('.staff-driver-link').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onSelectDriver) return;
				const driverName = btn.getAttribute('data-driver-name');
				if (!driverName) return;
				this.onSelectDriver(driverName);
			});
		});

		if (drivers.length === 0) {
			this.container.innerHTML = '<p style="color: #64748b;">No drivers assigned.</p>';
		}

		this.renderOperationalDepartment(data, this.activeOperationalTab);
		this.renderCommercial(data);
		this.renderManagement(data);
	}
}
