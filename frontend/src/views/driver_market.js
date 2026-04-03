import { renderFlagLabel } from './flags.js';

export default class DriverMarketView {
	constructor() {
		this.view = document.getElementById('driver-market-view');
		this.title = document.getElementById('driver-market-title');
		this.tableBody = document.getElementById('driver-market-table-body');
		this.headRow = document.querySelector('#driver-market-view thead tr');
		this.backBtn = document.getElementById('driver-market-back-btn');
		this.outgoingDriver = null;
		this.outgoingManager = null;
		this.outgoingSponsor = null;
		this.outgoingSupplier = null;
		this.outgoingRoleLabel = 'Driver';
		this.marketType = 'driver';
		this.onSign = null;
		this.onBack = null;
		this.bind();
	}

	bind() {
		if (this.backBtn) {
			this.backBtn.addEventListener('click', () => {
				if (this.onBack) this.onBack();
			});
		}
	}

	setSignHandler(handler) {
		this.onSign = handler;
	}

	setBackHandler(handler) {
		this.onBack = handler;
	}

	render(payload) {
		if (!this.tableBody || !this.title) return;
		this.marketType = payload?.market_type === 'commercial_manager' || payload?.market_type === 'technical_director' || payload?.market_type === 'title_sponsor' || payload?.market_type === 'tyre_supplier'
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
					: this.marketType === 'tyre_supplier'
						? 'Tyre Supplier'
					: 'Driver';
		const outgoingName = this.marketType === 'commercial_manager' || this.marketType === 'technical_director'
			? (this.outgoingManager?.name || this.outgoingRoleLabel)
			: this.marketType === 'title_sponsor'
				? (this.outgoingSponsor?.name || this.outgoingRoleLabel)
				: this.marketType === 'tyre_supplier'
					? (this.outgoingSupplier?.name || this.outgoingRoleLabel)
			: (this.outgoingDriver?.name || 'Driver');
		this.title.textContent = `Replace ${outgoingName}`;
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
			} else {
				this.headRow.innerHTML = `
					<th>Driver</th>
					<th>Age</th>
					<th>Country</th>
					<th>Speed</th>
					<th>Wage</th>
					<th>Action</th>
				`;
			}
		}

		const candidates = payload?.candidates || [];
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
			} else {
				const absWage = Math.abs(candidate.wage || 0);
				const wageText = `$${absWage.toLocaleString()}${candidate.pay_driver ? ' (Pay Driver)' : ''}`;
				tr.innerHTML = `
					<td>${candidate.name}</td>
					<td>${candidate.age}</td>
					<td>${renderFlagLabel(candidate.country, candidate.country)}</td>
					<td>${candidate.speed}</td>
					<td>${wageText}</td>
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
				} else if (this.marketType === 'tyre_supplier') {
					if (!this.outgoingSupplier) return;
					this.onSign(this.outgoingSupplier.name, incomingId, this.marketType);
				} else {
					if (!this.outgoingDriver) return;
					this.onSign(this.outgoingDriver.id, incomingId, this.marketType);
				}
			});
		});
	}
}
