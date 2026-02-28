import { renderFlagLabel } from './flags.js';

export default class DriverMarketView {
	constructor() {
		this.view = document.getElementById('driver-market-view');
		this.title = document.getElementById('driver-market-title');
		this.tableBody = document.getElementById('driver-market-table-body');
		this.backBtn = document.getElementById('driver-market-back-btn');
		this.outgoingDriver = null;
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
		this.outgoingDriver = payload?.outgoing_driver || null;
		const outgoingName = this.outgoingDriver?.name || 'Driver';
		this.title.textContent = `Replace ${outgoingName}`;

		const candidates = payload?.candidates || [];
		this.tableBody.innerHTML = '';
		if (!candidates.length) {
			const row = document.createElement('tr');
			row.innerHTML = '<td colspan="6">No available free agents</td>';
			this.tableBody.appendChild(row);
			return;
		}

		candidates.forEach((driver) => {
			const tr = document.createElement('tr');
			const absWage = Math.abs(driver.wage || 0);
			const wageText = `$${absWage.toLocaleString()}${driver.pay_driver ? ' (Pay Driver)' : ''}`;
			tr.innerHTML = `
				<td>${driver.name}</td>
				<td>${driver.age}</td>
				<td>${renderFlagLabel(driver.country, driver.country)}</td>
				<td>${driver.speed}</td>
				<td>${wageText}</td>
				<td><button class="driver-market-sign-btn" data-driver-id="${driver.id}">Sign</button></td>
			`;
			this.tableBody.appendChild(tr);
		});

		this.tableBody.querySelectorAll('.driver-market-sign-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				if (!this.onSign || !this.outgoingDriver) return;
				const incomingId = Number(btn.getAttribute('data-driver-id'));
				if (!Number.isFinite(incomingId)) return;
				this.onSign(this.outgoingDriver.id, incomingId);
			});
		});
	}
}
