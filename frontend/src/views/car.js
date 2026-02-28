/**
 * Car View Module
 * Displays team car speed comparison.
 */
export default class CarView {
	constructor() {
		this.body = document.getElementById('car-table-body');
		this.devBody = document.getElementById('car-development-table-body');
		this.currentSpeed = document.getElementById('car-development-current-speed');
		this.devStatus = document.getElementById('car-development-status');
		this.comparisonContent = document.getElementById('car-content-comparison');
		this.developmentContent = document.getElementById('car-content-development');
		this.tabButtons = document.querySelectorAll('.car-tab-btn');
		this.onStartDevelopment = null;
		this.activeTab = 'comparison';
		this.bindTabs();
	}

	setStartDevelopmentHandler(handler) {
		this.onStartDevelopment = handler;
	}

	bindTabs() {
		if (!this.tabButtons || this.tabButtons.length === 0) return;
		this.tabButtons.forEach((btn) => {
			btn.addEventListener('click', () => this.setActiveTab(btn.getAttribute('data-type') || 'comparison'));
		});
	}

	setActiveTab(tab) {
		this.activeTab = tab;
		this.tabButtons.forEach((btn) => {
			btn.classList.toggle('active', btn.getAttribute('data-type') === tab);
		});
		if (this.comparisonContent) {
			this.comparisonContent.style.display = tab === 'comparison' ? 'block' : 'none';
		}
		if (this.developmentContent) {
			this.developmentContent.style.display = tab === 'development' ? 'block' : 'none';
		}
	}

	getSpeedRating(speed, scaleMax = 100) {
		const numericSpeed = Number(speed);
		const value = Number.isFinite(numericSpeed) ? Math.max(0, numericSpeed) : 0;
		const maxValue = Math.max(1, Number(scaleMax) || 1);
		return Math.max(1, Math.min(5, Math.ceil((value / maxValue) * 5)));
	}

	renderRatingBlocks(value, label, scaleMax = 100) {
		const rating = this.getSpeedRating(value, scaleMax);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="car-speed-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="car-speed-rating" role="img" aria-label="${label} rating ${rating} out of 5">${blocks}</span>`;
	}

	render(data) {
		if (!this.body || !this.devBody) return;
		const teams = (data?.teams || []).slice().sort((a, b) => (b.car_speed ?? 0) - (a.car_speed ?? 0));
		const maxCarSpeed = Math.max(1, ...teams.map((t) => Number(t.car_speed || 0)));
		const maxEnginePower = Math.max(1, ...teams.map((t) => Number(t.engine_power || 0)));

		this.body.innerHTML = '';
		teams.forEach((team, index) => {
			const row = document.createElement('tr');
			row.innerHTML = `
				<td>${index + 1}</td>
				<td>${team.name}</td>
				<td>${team.country || '-'}</td>
				<td>${this.renderRatingBlocks(team.car_speed, 'Car speed', maxCarSpeed)}</td>
				<td>${this.renderRatingBlocks(team.engine_power || 0, 'Engine power', maxEnginePower)}</td>
			`;
			this.body.appendChild(row);
		});

		const project = data?.player_development || { active: false };
		if (this.currentSpeed) {
			const value = Number(data?.player_car_speed || 0);
			this.currentSpeed.innerHTML = `Current Car Rating: <strong>${value}</strong> ${this.renderRatingBlocks(value, 'Player car speed', maxCarSpeed)}`;
		}
		if (this.devStatus) {
			if (project.active) {
				this.devStatus.textContent = `Active project: ${String(project.development_type || '').toUpperCase()} | ${project.weeks_remaining}/${project.total_weeks} weeks remaining | Weekly cost $${Number(project.weekly_cost || 0).toLocaleString()} | Paid $${Number(project.paid || 0).toLocaleString()} of $${Number(project.total_cost || 0).toLocaleString()}`;
			} else {
				this.devStatus.textContent = 'No active development project';
			}
		}

		const catalog = data?.development_catalog || [];
		this.devBody.innerHTML = '';
		catalog.forEach((item) => {
			const row = document.createElement('tr');
			const disabled = project.active ? 'disabled' : '';
			row.innerHTML = `
				<td>${String(item.type || '').toUpperCase()}</td>
				<td>${item.weeks} weeks</td>
				<td>$${Number(item.weekly_cost || 0).toLocaleString()}</td>
				<td>+${item.speed_delta}</td>
				<td><button class="btn-secondary car-dev-btn" data-dev-type="${item.type}" ${disabled}>Start</button></td>
			`;
			this.devBody.appendChild(row);
		});

		this.devBody.querySelectorAll('.car-dev-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onStartDevelopment) return;
				const type = btn.getAttribute('data-dev-type');
				this.onStartDevelopment(type);
			});
		});

		this.setActiveTab(this.activeTab);
	}
}
