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
		this.tyresContent = document.getElementById('car-content-tyres');
		this.constructionContent = document.getElementById('car-content-construction');
		this.chassisContent = document.getElementById('car-content-chassis');
		this.tyresSuppliers = document.getElementById('car-tyres-suppliers');
		this.chassisBody = document.getElementById('car-chassis-table-body');
		this.raceAssignmentsStatus = document.getElementById('car-garage-race-assignments-status');
		this.mechanicsStatus = document.getElementById('car-garage-mechanics-status');
		this.sparesWidget = document.getElementById('car-spares-widget');
		this.constructionProjectsCard = document.getElementById('car-construction-projects-card');
		this.constructionBuildCard = document.getElementById('car-construction-build-card');
		this.tabButtons = document.querySelectorAll('.car-tab-btn');
		this.onStartDevelopment = null;
		this.onFinishDevelopmentStage = null;
		this.onSetDevelopmentAllocation = null;
		this.onSetConstructionAllocation = null;
		this.onStartConstruction = null;
		this.onSetTestChassis = null;
		this.onSetRaceChassisAssignments = null;
		this.onRepairChassisWear = null;
		this.onBuildSpareSet = null;
		this.playerSpares = 0;
		this.mechanicsCapacityRemaining = 100;
		this.mechanicsStaffAvailable = 0;
		this.mechanicsPercentPerSpare = 11;
		this.activeTab = 'comparison';
		this.bindTabs();
	}

	setStartDevelopmentHandler(handler) {
		this.onStartDevelopment = handler;
	}

	setFinishDevelopmentStageHandler(handler) {
		this.onFinishDevelopmentStage = handler;
	}

	setDevelopmentAllocationHandler(handler) {
		this.onSetDevelopmentAllocation = handler;
	}

	setConstructionAllocationHandler(handler) {
		this.onSetConstructionAllocation = handler;
	}

	setStartConstructionHandler(handler) {
		this.onStartConstruction = handler;
	}

	setTestChassisHandler(handler) {
		this.onSetTestChassis = handler;
	}

	setRaceChassisAssignmentsHandler(handler) {
		this.onSetRaceChassisAssignments = handler;
	}

	setRepairChassisWearHandler(handler) {
		this.onRepairChassisWear = handler;
	}

	setBuildSpareSetHandler(handler) {
		this.onBuildSpareSet = handler;
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
		if (this.constructionContent) {
			this.constructionContent.style.display = tab === 'construction' ? 'block' : 'none';
		}
		if (this.tyresContent) {
			this.tyresContent.style.display = tab === 'tyres' ? 'block' : 'none';
		}
		if (this.chassisContent) {
			this.chassisContent.style.display = tab === 'chassis' ? 'block' : 'none';
		}
	}

	getSpeedRating(speed, scaleMax = 100) {
		const numericSpeed = Number(speed);
		const value = Number.isFinite(numericSpeed) ? Math.max(0, numericSpeed) : 0;
		const maxValue = Math.max(1, Number(scaleMax) || 1);
		return Math.max(1, Math.min(5, Math.ceil((value / maxValue) * 5)));
	}

	getTyreQualityRating(value) {
		const numericValue = Number(value);
		const score = Number.isFinite(numericValue) ? Math.max(0, Math.min(100, numericValue)) : 0;
		if (score >= 90) return 5;
		if (score >= 80) return 4;
		if (score >= 70) return 3;
		if (score >= 60) return 2;
		return 1;
	}

	renderRatingBlocks(value, label, scaleMax = 100, ratingOverride = null) {
		const rating = ratingOverride ?? this.getSpeedRating(value, scaleMax);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="car-speed-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="car-speed-rating" role="img" aria-label="${label} rating ${rating} out of 5">${blocks}</span>`;
	}

	renderAvailabilityBlocks(value, label, maxValue = 10) {
		const filled = Math.max(0, Math.min(maxValue, Number(value || 0)));
		let blocks = '';
		for (let i = 1; i <= maxValue; i += 1) {
			const stateClass = i <= filled ? 'is-filled' : '';
			blocks += `<span class="car-speed-block car-availability-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="car-speed-rating car-availability-rating" role="img" aria-label="${label} ${filled} out of ${maxValue}">${blocks}</span>`;
	}

	renderProgressBlocks(value, label, maxValue = 10) {
		const filled = Math.max(0, Math.min(maxValue, Number(value || 0)));
		let blocks = '';
		for (let i = 1; i <= maxValue; i += 1) {
			const stateClass = i <= filled ? 'is-filled' : '';
			blocks += `<span class="car-speed-block car-development-progress-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="car-speed-rating car-development-progress" role="img" aria-label="${label} ${filled} out of ${maxValue}">${blocks}</span>`;
	}

	renderTyreSuppliers(tyreData = {}, scaleMax = 100) {
		if (!this.tyresSuppliers) return;
		const suppliers = Array.isArray(tyreData.suppliers) ? tyreData.suppliers : [];
		if (!suppliers.length) {
			this.tyresSuppliers.innerHTML = '<div class="car-tyre-supplier-card"><div class="car-construction-note">No tyre compound data available for this season.</div></div>';
			return;
		}
		this.tyresSuppliers.innerHTML = suppliers.map((supplier) => `
			<section class="car-tyre-supplier-card ${supplier.is_player_supplier ? 'is-player-supplier' : ''}">
				<div class="car-tyre-supplier-head">
					<div>
						<div class="car-tyre-supplier-name">${supplier.name}${supplier.is_player_supplier ? ' <span class="car-tyre-badge">Current Supplier</span>' : ''}</div>
						<div class="car-tyre-supplier-country">${supplier.country || '-'}</div>
					</div>
				</div>
				<div class="car-tyre-supplier-stats">
					<div><span>Resources</span>${this.renderRatingBlocks(supplier.resources, `${supplier.name} resources`, scaleMax)}</div>
					<div><span>Innovation</span>${this.renderRatingBlocks(supplier.innovation, `${supplier.name} innovation`, scaleMax)}</div>
					<div><span>Reliability</span>${this.renderRatingBlocks(supplier.reliability, `${supplier.name} reliability`, scaleMax)}</div>
				</div>
				<table class="data-table car-tyre-compound-table">
					<thead>
						<tr>
							<th>Compound</th>
							<th>Grip</th>
							<th>Wear</th>
							<th>Stiffness</th>
						</tr>
					</thead>
					<tbody>
						${(supplier.compounds || []).map((compound) => `
							<tr>
								<td><strong>${compound.name}</strong></td>
								<td>${this.renderRatingBlocks(compound.grip, `${supplier.name} ${compound.name} grip`, scaleMax, this.getTyreQualityRating(compound.grip))}</td>
								<td>${this.renderRatingBlocks(compound.wear, `${supplier.name} ${compound.name} wear`, scaleMax, this.getTyreQualityRating(compound.wear))}</td>
								<td>${this.renderRatingBlocks(compound.stiffness, `${supplier.name} ${compound.name} stiffness`, scaleMax, this.getTyreQualityRating(compound.stiffness))}</td>
							</tr>
						`).join('')}
					</tbody>
				</table>
			</section>
		`).join('');
	}

	updateSparesWidget(playerSpares) {
		this.playerSpares = Math.max(0, Math.min(10, Number(playerSpares || 0)));
		if (!this.sparesWidget) return;
		this.sparesWidget.innerHTML = `
			<div class="car-spares-widget-label">Available Spares</div>
			<div class="car-spares-widget-value">${this.renderAvailabilityBlocks(this.playerSpares, 'Available spares', 10)}</div>
			<div class="car-spares-widget-count">${this.playerSpares} / 10 sets</div>
		`;
	}

	applyChassisWearRepairResult(data) {
		if (!data) return;
		if (typeof data.spares_after !== 'undefined') {
			this.updateSparesWidget(data.spares_after);
		}
		if (typeof data.mechanics_usage_percent_after !== 'undefined') {
			this.mechanicsCapacityRemaining = Math.max(0, 100 - Number(data.mechanics_usage_percent_after || 0));
			if (this.mechanicsStatus) {
				this.mechanicsStatus.textContent = `${this.mechanicsCapacityRemaining}% remaining this week.`;
			}
		}
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

		const project = data?.player_development || { active: false, stages: [] };
		const projects = project.projects || {
			current_year: project,
			next_year: { active: false, scope: 'next_year', stages: [] },
		};
		const activeProjects = Object.values(projects).filter((item) => item?.active);
		if (this.currentSpeed) {
			const value = Number(data?.player_car_speed || 0);
			this.currentSpeed.innerHTML = `Current Car Rating: <strong>${value}</strong> ${this.renderRatingBlocks(value, 'Player car speed', maxCarSpeed)}`;
		}
		if (this.devStatus) {
			if (activeProjects.length) {
				this.devStatus.textContent = activeProjects.map((item) => `${item.name || 'Chassis Upgrade'}: ${Number(item.allocation_percent || 0)}%, ${item.current_stage_label || '-'}`).join(' | ');
			} else if (project.completed) {
				this.devStatus.textContent = `Completed project: ${project.name || 'Chassis Upgrade'} | Quality ${Number(project.quality_score || 0)} | Gain +${Number(project.projected_speed_delta || project.speed_delta || 0)}`;
			} else {
				this.devStatus.textContent = 'No active chassis design project';
			}
		}

		this.devBody.innerHTML = '';
		[
			{ scope: 'current_year', label: 'This Year Upgrade', startLabel: 'Start Upgrade' },
			{ scope: 'next_year', label: 'Next Year Chassis', startLabel: 'Start Next Car' },
		].forEach(({ scope, label, startLabel }) => {
			const scopedProject = projects[scope] || { active: false, scope, stages: [] };
			const projectName = scopedProject.name || label;
			const header = document.createElement('tr');
			header.className = 'car-development-project-row';
			header.innerHTML = `
				<td colspan="5">
					<strong>${projectName}</strong>
					<span class="car-development-project-meta">
						${scopedProject.active ? `Allocation ${Number(scopedProject.allocation_percent || 0)}% (${Number(scopedProject.assigned_designers || 0)} designers) | Projected +${Number(scopedProject.projected_speed_delta || 0)} | Risk ${scopedProject.risk || '-'}` : 'Not active'}
					</span>
				</td>
			`;
			this.devBody.appendChild(header);

			if (scopedProject.active) {
				const allocation = document.createElement('tr');
				const maxAllocation = Math.max(0, Math.min(100, Number(scopedProject.available_allocation_percent ?? 100)));
				const currentAllocation = Math.max(0, Math.min(maxAllocation, Number(scopedProject.allocation_percent || 0)));
				allocation.innerHTML = `
					<td>Designers</td>
					<td colspan="4">
						<input type="range" min="0" max="${maxAllocation}" step="5" value="${currentAllocation}" class="car-dev-allocation-slider" data-dev-scope="${scope}">
						<strong class="car-dev-allocation-value" data-dev-scope="${scope}">${currentAllocation}%</strong>
						<span class="car-development-project-meta">Max available: ${maxAllocation}%</span>
					</td>
				`;
				this.devBody.appendChild(allocation);
			}

			const stages = Array.isArray(scopedProject.stages) ? scopedProject.stages : [];
			stages.forEach((stage, index) => {
				const row = document.createElement('tr');
				const isCurrent = scopedProject.active && index === Number(scopedProject.current_stage_index || 0);
				const status = stage.completed ? 'Complete' : (isCurrent ? 'In Progress' : 'Pending');
				row.innerHTML = `
					<td>${stage.label || stage.key || '-'}</td>
					<td>${this.renderProgressBlocks(stage.progress, `${stage.label || stage.key} progress`)}</td>
					<td>${Number(stage.progress || 0)} / 10</td>
					<td>${status}</td>
					<td>${isCurrent ? `<button class="btn-secondary car-dev-finish-stage-btn" data-dev-scope="${scope}" ${scopedProject.can_finish_stage ? '' : 'disabled'}>${scopedProject.finish_action_label || 'Finish Stage'}</button>` : ''}</td>
				`;
				this.devBody.appendChild(row);
			});

			if (!scopedProject.active && !scopedProject.completed) {
				const row = document.createElement('tr');
				row.innerHTML = `
					<td colspan="4">${scope === 'next_year' ? 'Begin next season chassis design.' : 'Start a current-year chassis upgrade.'}</td>
					<td><button class="btn-secondary car-dev-btn" data-dev-type="${scope}">${startLabel}</button></td>
				`;
				this.devBody.appendChild(row);
			}
		});

		this.devBody.querySelectorAll('.car-dev-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onStartDevelopment) return;
				this.onStartDevelopment(btn.getAttribute('data-dev-type') || 'current_year');
			});
		});
		this.devBody.querySelectorAll('.car-dev-finish-stage-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onFinishDevelopmentStage) return;
				this.onFinishDevelopmentStage(btn.getAttribute('data-dev-scope') || 'current_year');
			});
		});
		this.devBody.querySelectorAll('.car-dev-allocation-slider').forEach((slider) => {
			slider.addEventListener('input', () => {
				const scope = slider.getAttribute('data-dev-scope') || 'current_year';
				const valueNode = this.devBody.querySelector(`.car-dev-allocation-value[data-dev-scope="${scope}"]`);
				if (valueNode) valueNode.textContent = `${Number(slider.value || 0)}%`;
			});
			slider.addEventListener('change', () => {
				if (!this.onSetDevelopmentAllocation) return;
				const scope = slider.getAttribute('data-dev-scope') || 'current_year';
				this.onSetDevelopmentAllocation(scope, Number(slider?.value || 0));
			});
		});

		this.renderTyreSuppliers(data?.tyres || {}, 100);

		const chassisRows = Array.isArray(data?.player_chassis) ? data.player_chassis : [];
		const playerDrivers = Array.isArray(data?.player_drivers) ? data.player_drivers : [];
		const driverOptions = playerDrivers.map((driver) => ({ value: String(driver.id), label: driver.name }));
		const playerSpares = Math.max(0, Math.min(10, Number(data?.player_spares || 0)));
		this.playerSpares = playerSpares;
		const spareConstruction = data?.construction?.spares || {};
		const constructionProjects = data?.construction?.projects || { projects: {} };
		const maintenance = data?.maintenance || {};
		const averageWearRepairPerSpare = 26;
		this.mechanicsCapacityRemaining = Math.max(0, Number(maintenance.mechanics_capacity_remaining ?? 100));
		this.mechanicsStaffAvailable = Math.max(0, Number(maintenance.mechanics_staff_available ?? 0));
		this.mechanicsPercentPerSpare = Math.max(0, Number(maintenance.mechanics_required_percent_per_spare ?? 11));

		if (this.chassisBody) {
			this.chassisBody.innerHTML = '';
			chassisRows.forEach((chassis) => {
				const repairDisabled = Number(chassis.wear || 0) <= 0 ? 'disabled' : '';
				const row = document.createElement('tr');
				row.innerHTML = `
					<td><strong>${chassis.name}</strong></td>
					<td>${Number(chassis.wear || 0)}</td>
					<td>
						<label class="car-chassis-radio">
							<input
								type="radio"
								name="car-test-chassis"
								class="car-chassis-test-radio"
								value="${chassis.id}"
								${chassis.assigned_to_test ? 'checked' : ''}
							>
							<span>Selected</span>
						</label>
					</td>
					<td>
						<select class="car-chassis-assignment-select" data-chassis-id="${chassis.id}">
							<option value="">Unassigned</option>
							${driverOptions.map((driver) => `<option value="${driver.value}" ${String(chassis.assigned_driver_id || '') === driver.value ? 'selected' : ''}>${driver.label}</option>`).join('')}
						</select>
					</td>
					<td>${Math.round(Number(chassis.mechanical_fail_probability || 0) * 100)}%</td>
					<td>
						<div class="car-chassis-maintenance">
							<input
								type="range"
								min="0"
								max="${Math.max(0, Number(chassis.wear || 0))}"
								value="0"
								step="1"
								class="car-chassis-repair-slider"
								data-chassis-id="${chassis.id}"
							>
							<div class="car-chassis-maintenance-meta">
								<span class="car-chassis-repair-value" data-chassis-id="${chassis.id}">0 wear</span>
								<span class="car-chassis-repair-cost" data-chassis-id="${chassis.id}">$0</span>
								<span class="car-chassis-repair-spares" data-chassis-id="${chassis.id}">0 spare sets</span>
								<span class="car-chassis-repair-mechanics" data-chassis-id="${chassis.id}">0% mechanics</span>
							</div>
							<button class="btn-secondary car-chassis-repair-btn" data-chassis-id="${chassis.id}" ${repairDisabled}>Repair</button>
						</div>
					</td>
				`;
				this.chassisBody.appendChild(row);
			});
			if (!chassisRows.length) {
				this.chassisBody.innerHTML = '<tr><td colspan="6">No chassis configured</td></tr>';
			}
		}
		if (this.mechanicsStatus) {
			this.mechanicsStatus.textContent = `${this.mechanicsCapacityRemaining}% remaining this week.`;
		}

		const refreshRaceStatus = () => {
			const selections = Array.from(document.querySelectorAll('.car-chassis-assignment-select'))
				.map((select) => ({
					chassisId: Number(select.dataset.chassisId),
					driverId: select.value ? Number(select.value) : null,
				}))
				.filter((item) => item.driverId);
			const uniqueDriverIds = new Set(selections.map((item) => item.driverId));
			const complete = selections.length === playerDrivers.length && uniqueDriverIds.size === playerDrivers.length;
			if (this.raceAssignmentsStatus) {
				this.raceAssignmentsStatus.textContent = complete
					? 'Race chassis assigned.'
					: 'Assign one distinct chassis to each driver.';
			}
			return complete ? selections : [];
		};

		document.querySelectorAll('.car-chassis-test-radio').forEach((input) => {
			input.addEventListener('change', () => {
				if (input.checked && this.onSetTestChassis) {
					this.onSetTestChassis(Number(input.value));
				}
			});
		});

		document.querySelectorAll('.car-chassis-assignment-select').forEach((select) => {
			select.addEventListener('change', () => {
				if (!select.value) {
					refreshRaceStatus();
					return;
				}
				document.querySelectorAll('.car-chassis-assignment-select').forEach((otherSelect) => {
					if (otherSelect !== select && otherSelect.value === select.value) {
						otherSelect.value = '';
					}
				});
				const assignments = refreshRaceStatus();
				if (assignments.length === 2 && this.onSetRaceChassisAssignments) {
					const orderedAssignments = playerDrivers.map((driver) => assignments.find((item) => item.driverId === driver.id));
					if (orderedAssignments.every(Boolean)) {
						this.onSetRaceChassisAssignments(orderedAssignments[0].chassisId, orderedAssignments[1].chassisId);
					}
				}
			});
		});
		refreshRaceStatus();

		document.querySelectorAll('.car-chassis-repair-slider').forEach((slider) => {
			const updateRepairPreview = () => {
				const value = Number(slider.value || 0);
				const chassisId = slider.dataset.chassisId;
				const valueNode = document.querySelector(`.car-chassis-repair-value[data-chassis-id="${chassisId}"]`);
				const costNode = document.querySelector(`.car-chassis-repair-cost[data-chassis-id="${chassisId}"]`);
				const sparesNode = document.querySelector(`.car-chassis-repair-spares[data-chassis-id="${chassisId}"]`);
				const mechanicsNode = document.querySelector(`.car-chassis-repair-mechanics[data-chassis-id="${chassisId}"]`);
				const repairBtn = document.querySelector(`.car-chassis-repair-btn[data-chassis-id="${chassisId}"]`);
				const estimatedSpares = value > 0 ? Math.max(1, Math.ceil(value / averageWearRepairPerSpare)) : 0;
				const estimatedMechanics = estimatedSpares * this.mechanicsPercentPerSpare;
				if (valueNode) valueNode.textContent = `${value} wear`;
				if (costNode) costNode.textContent = `$${(value * 3200).toLocaleString()}`;
				if (sparesNode) {
					sparesNode.textContent = estimatedSpares === 1 ? 'Est. 1 spare set' : `Est. ${estimatedSpares} spare sets`;
				}
				if (mechanicsNode) {
					mechanicsNode.textContent = `Est. ${estimatedMechanics}% mechanics`;
				}
				if (repairBtn) {
					repairBtn.disabled =
						value <= 0 ||
						this.playerSpares <= 0 ||
						estimatedSpares > this.playerSpares ||
						this.mechanicsStaffAvailable <= 0 ||
						estimatedMechanics > this.mechanicsCapacityRemaining;
				}
			};
			slider.addEventListener('input', updateRepairPreview);
			updateRepairPreview();
		});

		document.querySelectorAll('.car-chassis-repair-btn').forEach((button) => {
			button.addEventListener('click', () => {
				if (!this.onRepairChassisWear) return;
				const chassisId = Number(button.dataset.chassisId);
				const slider = document.querySelector(`.car-chassis-repair-slider[data-chassis-id="${chassisId}"]`);
				const wearPoints = Number(slider?.value || 0);
				if (wearPoints > 0) {
					this.onRepairChassisWear(chassisId, wearPoints);
				}
			});
		});

		this.updateSparesWidget(playerSpares);

		if (this.constructionBuildCard) {
			const buildCost = Number(spareConstruction.build_cost || 0);
			const canBuild = Boolean(spareConstruction.can_build);
			const blockingReason = spareConstruction.blocking_reason || 'Unable to build spare set';
			const requiredPercentage = Number(spareConstruction.engineering_required_percentage || 0);
			const requiredStaff = Number(spareConstruction.engineering_required_staff || 0);
			const availableStaff = Number(spareConstruction.engineering_staff_available || 0);
			const usagePercent = Number(spareConstruction.construction_usage_percent || 0);
			const remainingPercent = Number(spareConstruction.construction_capacity_remaining || 0);
			this.constructionBuildCard.innerHTML = `
				<div class="car-construction-build-head">
					<div>
						<div class="car-spares-widget-label">Build Spare Set</div>
						<div class="car-construction-build-title">Engineering Construction</div>
					</div>
					<div class="car-construction-build-cost">$${buildCost.toLocaleString()}</div>
				</div>
				<div class="car-construction-build-meta">
					<div>Engineering Required: <strong>${requiredStaff}</strong> staff (${requiredPercentage}%)</div>
					<div>Engineering Available: <strong>${availableStaff}</strong></div>
					<div>Capacity Used This Week: <strong>${usagePercent}%</strong></div>
					<div>Capacity Remaining: <strong>${remainingPercent}%</strong></div>
				</div>
				<div class="car-construction-note">${canBuild ? "A spare set can be built if you allocate this week's remaining construction capacity." : blockingReason}</div>
				<button id="car-build-spare-set-btn" class="btn-primary" ${canBuild ? '' : 'disabled'}>Build Spare Set</button>
			`;
			const buildBtn = document.getElementById('car-build-spare-set-btn');
			if (buildBtn) {
				buildBtn.addEventListener('click', () => {
					if (this.onBuildSpareSet) this.onBuildSpareSet();
				});
			}
		}

		if (this.constructionProjectsCard) {
			this.constructionProjectsCard.innerHTML = this.renderConstructionProjects(constructionProjects);
			this.constructionProjectsCard.querySelectorAll('.car-construction-start-btn').forEach((button) => {
				button.addEventListener('click', () => {
					if (!this.onStartConstruction) return;
					this.onStartConstruction(button.getAttribute('data-construction-scope') || 'current_year');
				});
			});
			this.constructionProjectsCard.querySelectorAll('.car-construction-allocation-slider').forEach((slider) => {
				slider.addEventListener('input', () => {
					const scope = slider.getAttribute('data-construction-scope') || 'current_year';
					const valueNode = this.constructionProjectsCard.querySelector(`.car-construction-allocation-value[data-construction-scope="${scope}"]`);
					if (valueNode) valueNode.textContent = `${Number(slider.value || 0)}%`;
				});
				slider.addEventListener('change', () => {
					if (!this.onSetConstructionAllocation) return;
					const scope = slider.getAttribute('data-construction-scope') || 'current_year';
					this.onSetConstructionAllocation(scope, Number(slider.value || 0));
				});
			});
		}

		this.setActiveTab(this.activeTab);
	}

	renderConstructionProjects(constructionProjects = {}) {
		const projects = constructionProjects.projects || {};
		const rows = [
			{ scope: 'current_year', label: 'This Year Upgrade' },
			{ scope: 'next_year', label: 'Next Year Chassis' },
		].map(({ scope, label }) => {
			const project = projects[scope] || {};
			const active = Boolean(project.active);
			const completed = Boolean(project.completed);
			const canStart = Boolean(project.can_start);
			const progress = Number(project.progress || 0);
			const progressRequired = Math.max(1, Number(project.progress_required || 10));
			const estimatedWeeks = Number(project.estimated_weeks || 0);
			const targetRange = Array.isArray(project.target_week_range) ? project.target_week_range : [];
			const targetWeeks = targetRange.length === 2 ? `${Math.round(Number(targetRange[0] || 0))}-${Math.round(Number(targetRange[1] || 0))} weeks` : '-';
			const maxAllocation = Math.max(0, Math.min(100, Number(project.available_allocation_percent ?? 100)));
			const currentAllocation = Math.max(0, Math.min(maxAllocation, Number(project.allocation_percent || 0)));
			if (!active && !completed && !canStart) {
				return `
					<section class="car-tyre-supplier-card">
						<div class="car-spares-widget-label">${label}</div>
						<div class="car-construction-note">No completed design is ready for construction.</div>
					</section>
				`;
			}
			return `
				<section class="car-tyre-supplier-card">
					<div class="car-construction-build-head">
						<div>
							<div class="car-spares-widget-label">${label}</div>
							<div class="car-construction-build-title">${project.name || label}</div>
						</div>
						<div class="car-construction-build-cost">$${Number(project.total_cost || 0).toLocaleString()}</div>
					</div>
					<div class="car-construction-build-meta">
						<div>Progress: <strong>${progress} / ${progressRequired}</strong></div>
						<div>Paid: <strong>$${Number(project.paid || 0).toLocaleString()}</strong></div>
						<div>Engineers: <strong>${Number(project.assigned_engineers || 0)}</strong></div>
						<div>Outcome: <strong>${scope === 'next_year' ? `${Number(project.race_ready_built || project.units_built || 0)} / ${Number(project.race_ready_required || 2)} race chassis` : `+${Number(project.speed_delta || 0)} speed`}</strong></div>
						<div>Target: <strong>${targetWeeks}</strong></div>
						<div>Estimate: <strong>${estimatedWeeks > 0 ? `${Math.ceil(estimatedWeeks)} weeks` : 'Assign engineers'}</strong></div>
					</div>
					<div>${this.renderProgressBlocks(progress, `${project.name || label} construction`, progressRequired)}</div>
					${canStart ? `
						<div class="car-construction-actions">
							<button class="btn-secondary car-construction-start-btn" data-construction-scope="${scope}">Start Construction</button>
						</div>
					` : ''}
					${active ? `
						<div class="car-construction-build-meta">
							<div>
								<input type="range" min="0" max="${maxAllocation}" step="5" value="${currentAllocation}" class="car-construction-allocation-slider" data-construction-scope="${scope}">
								<strong class="car-construction-allocation-value" data-construction-scope="${scope}">${currentAllocation}%</strong>
								<span class="car-development-project-meta">Max available: ${maxAllocation}%</span>
							</div>
						</div>
					` : (completed ? '<div class="car-construction-note">Construction complete.</div>' : '')}
				</section>
			`;
		}).join('');
		return `
			<div class="car-construction-projects">
				<div class="car-construction-section-head">
					<div>
						<div class="car-spares-widget-label">Build Queue</div>
						<div class="car-construction-build-title">Chassis Construction</div>
					</div>
				</div>
				<div class="car-construction-grid">${rows}</div>
			</div>
		`;
	}
}
