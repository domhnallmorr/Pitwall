import { renderFlagLabel, toFlagSlug } from './flags.js';

export default class DriverMarketView {
	constructor() {
		this.view = document.getElementById('driver-market-view');
		this.title = document.getElementById('driver-market-title');
		this.tableBody = document.getElementById('driver-market-table-body');
		this.headRow = document.querySelector('#driver-market-view thead tr');
		this.backBtn = document.getElementById('driver-market-back-btn');
		this.tableWrap = document.getElementById('driver-market-table-wrap');
		this.driverWorkspace = document.getElementById('driver-market-driver-workspace');
		this.driverList = document.getElementById('driver-market-driver-list');
		this.driverDetail = document.getElementById('driver-market-driver-detail');
		this.offerModal = document.getElementById('driver-market-offer-modal');
		this.offerTitle = document.getElementById('driver-market-offer-title');
		this.offerDriver = document.getElementById('driver-market-offer-driver');
		this.offerStatus = document.getElementById('driver-market-offer-status');
		this.offerContract = document.getElementById('driver-market-offer-contract');
		this.offerSalary = document.getElementById('driver-market-offer-salary');
		this.offerCancelBtn = document.getElementById('driver-market-offer-cancel-btn');
		this.offerConfirmBtn = document.getElementById('driver-market-offer-confirm-btn');
		this.resultModal = document.getElementById('driver-market-result-modal');
		this.resultKicker = document.getElementById('driver-market-result-kicker');
		this.resultTitle = document.getElementById('driver-market-result-title');
		this.resultMessage = document.getElementById('driver-market-result-message');
		this.resultMeta = document.getElementById('driver-market-result-meta');
		this.resultCloseBtn = document.getElementById('driver-market-result-close-btn');
		this.outgoingDriver = null;
		this.outgoingManager = null;
		this.outgoingSponsor = null;
		this.outgoingSupplier = null;
		this.outgoingRoleLabel = 'Driver';
		this.marketType = 'driver';
		this.onSign = null;
		this.onBack = null;
		this.currentCandidates = [];
		this.selectedCandidateId = null;
		this.onResultClose = null;
		this.bind();
	}

	bind() {
		if (this.backBtn) {
			this.backBtn.addEventListener('click', () => {
				if (this.onBack) this.onBack();
			});
		}
		if (this.offerCancelBtn) {
			this.offerCancelBtn.addEventListener('click', () => this.closeOfferModal());
		}
		if (this.offerModal) {
			this.offerModal.addEventListener('click', (event) => {
				if (event.target === this.offerModal) {
					this.closeOfferModal();
				}
			});
		}
		if (this.resultCloseBtn) {
			this.resultCloseBtn.addEventListener('click', () => this.closeResultModal());
		}
		if (this.resultModal) {
			this.resultModal.addEventListener('click', (event) => {
				if (event.target === this.resultModal) {
					this.closeResultModal();
				}
			});
		}
		if (this.offerConfirmBtn) {
			this.offerConfirmBtn.addEventListener('click', () => {
				if (!this.onSign || this.marketType !== 'driver' || !this.outgoingDriver) return;
				const candidate = this.getSelectedCandidate();
				if (!candidate) return;
				const availability = this.getDriverCandidateAvailability(candidate);
				if (!availability.targetable) return;
				this.onSign(this.outgoingDriver.id, candidate.id, this.marketType, {
					salary: Number(this.offerSalary?.value || 0),
					contract_length: Number(this.offerContract?.value || 0),
				});
				this.closeOfferModal();
			});
		}
	}

	setSignHandler(handler) {
		this.onSign = handler;
	}

	setBackHandler(handler) {
		this.onBack = handler;
	}

	getDriverCandidateAvailability(candidate) {
		const yearsLeft = Number(candidate?.contract_length ?? 0);
		if (yearsLeft === 1) {
			return {
				label: 'Expiring Contract',
				className: 'is-expiring',
				targetable: true,
			};
		}
		const currentTeam = candidate?.team_name || candidate?.team || '';
		if (!currentTeam) {
			return {
				label: 'Free Agent',
				className: 'is-free-agent',
				targetable: true,
			};
		}
		return {
			label: 'Under Contract',
			className: 'is-unavailable',
			targetable: false,
		};
	}

	getSuggestedSalary(candidate) {
		const base = Math.abs(Number(candidate?.wage) || 0);
		if (base > 0) return base;
		const speed = Number(candidate?.speed) || 0;
		return Math.max(250000, speed * 20000);
	}

	getDriverRating(speed) {
		const numericSpeed = Number(speed);
		const clamped = Number.isFinite(numericSpeed) ? Math.max(0, Math.min(100, numericSpeed)) : 0;
		return Math.max(1, Math.ceil(clamped / 20));
	}

	renderSpeedBlocks(speed) {
		const rating = this.getDriverRating(speed);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="staff-speed-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="staff-speed-rating" role="img" aria-label="Speed rating ${rating} out of 5">${blocks}</span>`;
	}

	renderFlagIcon(country) {
		const safeCountry = country || 'Unknown';
		const flagSlug = toFlagSlug(safeCountry);
		const primarySrc = `assets/flags/${encodeURIComponent(safeCountry)}.png`;
		const fallbackSrc = `assets/flags/${flagSlug}.png`;
		return `<img class="app-flag driver-market-inline-flag" src="${primarySrc}" alt="${safeCountry} flag" onerror="if(!this.dataset.fallback){this.dataset.fallback='1';this.src='${fallbackSrc}';}else{this.style.display='none';}">`;
	}

	getSelectedCandidate() {
		return this.currentCandidates.find((candidate) => candidate.id === this.selectedCandidateId) || null;
	}

	setSelectedCandidate(candidateId) {
		this.selectedCandidateId = candidateId;
		this.renderDriverList();
		this.renderDriverDetail();
	}

	openOfferModal() {
		const candidate = this.getSelectedCandidate();
		if (!candidate || !this.offerModal) return;
		const availability = this.getDriverCandidateAvailability(candidate);
		if (!availability.targetable) return;
		if (this.offerTitle) this.offerTitle.textContent = `Offer ${candidate.name}`;
		if (this.offerDriver) this.offerDriver.textContent = candidate.name;
		if (this.offerStatus) {
			const currentTeam = candidate.team_name || candidate.team || 'Free Agent';
			this.offerStatus.textContent = availability.label === 'Expiring Contract'
				? `${availability.label} at ${currentTeam}`
				: availability.label;
		}
		if (this.offerContract) this.offerContract.value = '2';
		if (this.offerSalary) this.offerSalary.value = String(this.getSuggestedSalary(candidate));
		this.offerModal.style.display = 'flex';
	}

	closeOfferModal() {
		if (this.offerModal) this.offerModal.style.display = 'none';
	}

	showOfferResult(result = {}, onClose = null) {
		if (!this.resultModal) return false;
		const accepted = Boolean(result.accepted);
		this.onResultClose = typeof onClose === 'function' ? onClose : null;
		if (this.resultKicker) this.resultKicker.textContent = accepted ? 'Offer Accepted' : 'Offer Declined';
		if (this.resultTitle) this.resultTitle.textContent = accepted ? 'Deal Agreed' : 'Offer Rejected';
		if (this.resultMessage) this.resultMessage.textContent = result.message || 'Driver offer processed.';
		if (this.resultMeta) {
			const meta = [];
			if (result.driver_name) meta.push(`<div><span>Driver</span><strong>${result.driver_name}</strong></div>`);
			if (result.interest_band) meta.push(`<div><span>Interest</span><strong>${result.interest_band}</strong></div>`);
			if (Number.isFinite(Number(result.salary))) meta.push(`<div><span>Salary</span><strong>$${Math.abs(Number(result.salary)).toLocaleString()}</strong></div>`);
			if (Number.isFinite(Number(result.contract_length))) meta.push(`<div><span>Term</span><strong>${Number(result.contract_length)} year${Number(result.contract_length) === 1 ? '' : 's'}</strong></div>`);
			this.resultMeta.innerHTML = meta.join('');
		}
		if (this.resultCloseBtn) {
			this.resultCloseBtn.textContent = accepted ? 'Return to Staff' : 'Continue Browsing';
		}
		this.resultModal.style.display = 'flex';
		return true;
	}

	closeResultModal() {
		if (this.resultModal) this.resultModal.style.display = 'none';
		const callback = this.onResultClose;
		this.onResultClose = null;
		if (callback) callback();
	}

	renderDriverList() {
		if (!this.driverList) return;
		this.driverList.innerHTML = '';
		if (!this.currentCandidates.length) {
			this.driverList.innerHTML = '<p class="driver-market-empty">No available candidates</p>';
			return;
		}

		this.currentCandidates.forEach((candidate) => {
			const item = document.createElement('button');
			item.type = 'button';
			item.className = `driver-market-list-item${candidate.id === this.selectedCandidateId ? ' is-active' : ''}`;
			item.innerHTML = `
				<div class="driver-market-list-row">
					${this.renderFlagIcon(candidate.country)}
					<span class="driver-market-list-name">${candidate.name} <span class="driver-market-list-age">(${candidate.age})</span></span>
					<span class="driver-market-list-rating">${this.renderSpeedBlocks(candidate.speed)}</span>
				</div>
			`;
			item.addEventListener('click', () => this.setSelectedCandidate(candidate.id));
			this.driverList.appendChild(item);
		});
	}

	renderDriverDetail() {
		if (!this.driverDetail) return;
		const candidate = this.getSelectedCandidate();
		if (!candidate) {
			this.driverDetail.innerHTML = '<div class="driver-market-empty">Select a driver to review their details.</div>';
			return;
		}

		const availability = this.getDriverCandidateAvailability(candidate);
		const currentTeam = candidate.team_name || candidate.team || 'Free Agent';
		const wageText = `$${Math.abs(candidate.wage || 0).toLocaleString()}${candidate.pay_driver ? ' (Pay Driver)' : ''}`;
		const portraitFile = encodeURIComponent(`${(candidate.name || '').toLowerCase()}.png`);
		const contractText = availability.label === 'Expiring Contract'
			? `Contract expires at the end of this season with ${currentTeam}.`
			: availability.label === 'Free Agent'
				? 'Currently unattached and available for immediate approach.'
				: `${Math.max(0, Number(candidate.contract_length || 0))} years remain with ${currentTeam}.`;

		this.driverDetail.innerHTML = `
			<div class="driver-market-detail-head">
				<div class="driver-market-detail-portrait">
					<img src="assets/drivers/${portraitFile}" alt="${candidate.name}" onerror="this.style.display='none'">
				</div>
				<div>
					<p class="home-kicker">Driver Profile</p>
					<h3>${candidate.name}</h3>
					<div class="driver-market-detail-subline">${renderFlagLabel(candidate.country, candidate.country)} &bull; Age ${candidate.age}</div>
				</div>
				<span class="driver-market-status ${availability.className}">${availability.label}</span>
			</div>
			<div class="driver-market-detail-grid">
				<div class="driver-market-detail-card">
					<span class="driver-market-detail-label">Current Team</span>
					<strong>${currentTeam}</strong>
				</div>
				<div class="driver-market-detail-card">
					<span class="driver-market-detail-label">Speed</span>
					<strong>${this.renderSpeedBlocks(candidate.speed)}</strong>
				</div>
				<div class="driver-market-detail-card">
					<span class="driver-market-detail-label">Current Ask</span>
					<strong>${wageText}</strong>
				</div>
				<div class="driver-market-detail-card">
					<span class="driver-market-detail-label">Contract Status</span>
					<strong>${contractText}</strong>
				</div>
			</div>
			<div class="driver-market-detail-actions">
				<button class="btn-primary driver-market-offer-btn" ${availability.targetable ? '' : 'disabled'}>Offer</button>
				<p class="driver-market-offer-inline-note">Offer terms are set in the modal after you choose to approach the driver.</p>
			</div>
		`;

		this.driverDetail.querySelector('.driver-market-offer-btn')?.addEventListener('click', () => this.openOfferModal());
	}

	renderLegacyTable(candidates) {
		if (!this.tableBody) return;
		this.tableBody.innerHTML = '';
		if (!candidates.length) {
			const row = document.createElement('tr');
			row.innerHTML = '<td colspan="6">No available candidates</td>';
			this.tableBody.appendChild(row);
			return;
		}

		candidates.forEach((candidate) => {
			const tr = document.createElement('tr');
			if (this.marketType === 'commercial_manager' || this.marketType === 'technical_director') {
				const absSalary = Math.abs(candidate.salary || 0);
				tr.innerHTML = `
					<td>${candidate.name}</td>
					<td>${candidate.age}</td>
					<td>${renderFlagLabel(candidate.country, candidate.country)}</td>
					<td>${candidate.skill}</td>
					<td>$${absSalary.toLocaleString()}</td>
					<td><button class="driver-market-sign-btn" data-driver-id="${candidate.id}">Sign</button></td>
				`;
			} else if (this.marketType === 'title_sponsor') {
				tr.innerHTML = `
					<td>${candidate.name}</td>
					<td>${candidate.wealth}</td>
					<td>${candidate.start_year || 'Default'}</td>
					<td><button class="driver-market-sign-btn" data-driver-id="${candidate.id}">Sign</button></td>
				`;
			} else if (this.marketType === 'tyre_supplier') {
				tr.innerHTML = `
					<td>${candidate.name}</td>
					<td>${renderFlagLabel(candidate.country, candidate.country)}</td>
					<td>${candidate.grip}</td>
					<td>${candidate.wear}</td>
					<td><button class="driver-market-sign-btn" data-driver-id="${candidate.id}">Sign</button></td>
				`;
			} else if (this.marketType === 'engine_supplier') {
				tr.innerHTML = `
					<td>${candidate.name}</td>
					<td>${renderFlagLabel(candidate.country, candidate.country)}</td>
					<td>${candidate.power}</td>
					<td>${candidate.resources}</td>
					<td><button class="driver-market-sign-btn" data-driver-id="${candidate.id}">Sign</button></td>
				`;
			}
			this.tableBody.appendChild(tr);
		});

		this.tableBody.querySelectorAll('.driver-market-sign-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onSign) return;
				const incomingId = Number(btn.getAttribute('data-driver-id'));
				if (!Number.isFinite(incomingId)) return;
				if (this.marketType === 'commercial_manager' || this.marketType === 'technical_director') {
					if (!this.outgoingManager) return;
					this.onSign(this.outgoingManager.id, incomingId, this.marketType);
				} else if (this.marketType === 'title_sponsor') {
					if (!this.outgoingSponsor) return;
					this.onSign(this.outgoingSponsor.name, incomingId, this.marketType);
				} else if (this.marketType === 'engine_supplier' || this.marketType === 'tyre_supplier') {
					if (!this.outgoingSupplier) return;
					this.onSign(this.outgoingSupplier.name, incomingId, this.marketType);
				}
			});
		});
	}

	render(payload) {
		if (!this.title) return;
		this.marketType = payload?.market_type === 'commercial_manager' || payload?.market_type === 'technical_director' || payload?.market_type === 'title_sponsor' || payload?.market_type === 'tyre_supplier' || payload?.market_type === 'engine_supplier'
			? payload.market_type
			: 'driver';
		this.outgoingDriver = payload?.outgoing_driver || null;
		this.outgoingManager = payload?.outgoing_manager || null;
		this.outgoingSponsor = payload?.outgoing_sponsor || null;
		this.outgoingSupplier = payload?.outgoing_supplier || null;
		this.outgoingRoleLabel = this.marketType === 'technical_director'
			? 'Technical Director'
			: this.marketType === 'commercial_manager'
				? 'Commercial Manager'
				: this.marketType === 'title_sponsor'
					? 'Title Sponsor'
					: this.marketType === 'engine_supplier'
						? 'Engine Supplier'
						: this.marketType === 'tyre_supplier'
							? 'Tyre Supplier'
							: 'Driver';
		const outgoingName = this.marketType === 'commercial_manager' || this.marketType === 'technical_director'
			? (this.outgoingManager?.name || this.outgoingRoleLabel)
			: this.marketType === 'title_sponsor'
				? (this.outgoingSponsor?.name || this.outgoingRoleLabel)
				: this.marketType === 'engine_supplier' || this.marketType === 'tyre_supplier'
					? (this.outgoingSupplier?.name || this.outgoingRoleLabel)
					: (this.outgoingDriver?.name || 'Driver');
		this.title.textContent = `Replace ${outgoingName}`;
		this.closeOfferModal();

		if (this.headRow) {
			if (this.marketType === 'commercial_manager' || this.marketType === 'technical_director') {
				this.headRow.innerHTML = `
					<th>Name</th>
					<th>Age</th>
					<th>Country</th>
					<th>Skill</th>
					<th>Salary</th>
					<th>Action</th>
				`;
			} else if (this.marketType === 'title_sponsor') {
				this.headRow.innerHTML = `
					<th>Name</th>
					<th>Wealth</th>
					<th>Market Since</th>
					<th>Action</th>
				`;
			} else if (this.marketType === 'tyre_supplier') {
				this.headRow.innerHTML = `
					<th>Name</th>
					<th>Country</th>
					<th>Grip</th>
					<th>Wear</th>
					<th>Action</th>
				`;
			} else if (this.marketType === 'engine_supplier') {
				this.headRow.innerHTML = `
					<th>Name</th>
					<th>Country</th>
					<th>Power</th>
					<th>Resources</th>
					<th>Action</th>
				`;
			}
		}

		const candidates = payload?.candidates || [];
		this.currentCandidates = this.marketType === 'driver'
			? [...candidates].sort((a, b) => (Number(b.speed) || 0) - (Number(a.speed) || 0) || String(a.name).localeCompare(String(b.name)))
			: candidates;

		if (this.marketType === 'driver') {
			if (this.driverWorkspace) this.driverWorkspace.style.display = 'grid';
			if (this.tableWrap) this.tableWrap.style.display = 'none';
			const firstCandidate = this.currentCandidates[0] || null;
			this.selectedCandidateId = firstCandidate ? firstCandidate.id : null;
			this.renderDriverList();
			this.renderDriverDetail();
			return;
		}

		if (this.driverWorkspace) this.driverWorkspace.style.display = 'none';
		if (this.tableWrap) this.tableWrap.style.display = 'block';
		this.renderLegacyTable(this.currentCandidates);
	}
}
