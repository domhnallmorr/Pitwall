function formatMoney(value, { signed = false } = {}) {
	const amount = Number(value || 0);
	const formatted = `$${Math.abs(amount).toLocaleString()}`;
	if (!signed) {
		return amount < 0 ? `-${formatted}` : formatted;
	}
	return amount >= 0 ? `+${formatted}` : `-${formatted}`;
}

export function renderTrackProfitLossHtml(rows = []) {
	if (!rows.length) {
		return '<tr><td colspan="6" style="text-align:center; color:#64748b;">No track-linked finance yet.</td></tr>';
	}

	return rows.map((rowData) => {
		const netClass = rowData.net >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
		return `
			<tr>
				<td>${rowData.track}</td>
				<td>${rowData.type || '-'}</td>
				<td>${rowData.country}</td>
				<td class="finance-amount-positive">$${(rowData.income || 0).toLocaleString()}</td>
				<td class="finance-amount-negative">$${(rowData.expense || 0).toLocaleString()}</td>
				<td class="${netClass}">${rowData.net >= 0 ? '+' : '-'}$${Math.abs(rowData.net || 0).toLocaleString()}</td>
			</tr>
		`;
	}).join('');
}

export function renderTransactionsHtml(transactions = []) {
	if (!transactions.length) {
		return '<tr><td colspan="4" style="text-align:center; color:#64748b;">No transactions yet.</td></tr>';
	}

	return [...transactions].reverse().map((t) => {
		const amountFormatted = '$' + Math.abs(t.amount).toLocaleString();
		const amountClass = t.amount >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
		const amountDisplay = t.amount >= 0 ? '+' + amountFormatted : '-' + amountFormatted;
		const categoryLabel = t.category.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
		const categoryClass = t.category === 'transport' ? 'finance-category-badge finance-category-transport' : 'finance-category-badge';

		return `
			<tr>
				<td>Week ${t.week}, ${t.year}</td>
				<td>${t.description}</td>
				<td><span class="${categoryClass}">${categoryLabel}</span></td>
				<td class="${amountClass}">${amountDisplay}</td>
			</tr>
		`;
	}).join('');
}

export function renderTitleSponsorNegotiationSupplierList(sponsors = []) {
	if (!sponsors.length) {
		return '<p class="finance-engine-negotiation-empty">No sponsors available.</p>';
	}
	return sponsors.map((sponsor) => `
		<div class="finance-engine-supplier-row">
			<div>
				<div class="finance-section-title">${sponsor.name}</div>
				<div class="finance-balance-label">Wealth ${sponsor.wealth}</div>
			</div>
			<button class="btn-secondary" data-title-sponsor-id="${sponsor.id}" ${sponsor.targetable ? '' : 'disabled'}>
				Approach
			</button>
		</div>
	`).join('');
}

export function renderEngineNegotiationSupplierList(suppliers = []) {
	if (!suppliers.length) {
		return '<p class="finance-engine-negotiation-empty">No suppliers available.</p>';
	}
	return suppliers.map((supplier) => `
		<div class="finance-engine-supplier-row">
			<div>
				<div class="finance-section-title">${supplier.name}</div>
				<div class="finance-balance-label">${supplier.country} · Power ${supplier.power} · Resources ${supplier.resources}</div>
			</div>
			<button class="btn-secondary" data-engine-supplier-id="${supplier.id}" ${supplier.targetable ? '' : 'disabled'}>
				Approach
			</button>
		</div>
	`).join('');
}

export function renderNegotiationBlockedState(reason) {
	return `
		<div class="finance-engine-negotiation-empty">
			<h3>Negotiations Unavailable</h3>
			<p>${reason}</p>
		</div>
	`;
}

export function renderNegotiationIdleState({ intro, commercialManager, commercialStaffTotal }) {
	return `
		<div class="finance-engine-negotiation-empty">
			<h3>No Active Negotiation</h3>
			<p>${intro}</p>
			<div class="finance-balance-label">Commercial Manager</div>
			<div>${commercialManager?.name || 'Unassigned'} · Skill ${commercialManager?.skill || 0}</div>
			<div class="finance-balance-label" style="margin-top:12px;">Commercial Staff Available</div>
			<div>${commercialStaffTotal || 0}</div>
		</div>
	`;
}

export function renderTitleSponsorNegotiationDetail(data = {}) {
	const active = data.active_negotiation;
	if (data.blocked_reason) {
		return renderNegotiationBlockedState(data.blocked_reason);
	}
	if (!active) {
		return renderNegotiationIdleState({
			intro: 'Select a sponsor on the left to begin talks. Commercial staff and your commercial manager will determine how quickly the deal progresses.',
			commercialManager: data.commercial_manager,
			commercialStaffTotal: data.commercial_staff_total,
		});
	}

	const boxes = Array.from({ length: active.total_boxes }, (_, index) => `
		<div class="finance-engine-progress-box ${(index + 1) <= active.progress_boxes ? 'filled' : ''}">
			<span>${index + 1}</span>
		</div>
	`).join('');

	return `
		<div class="finance-engine-negotiation-card">
			<div class="finance-balance-label">Active Negotiation</div>
			<h3>${active.sponsor_name}</h3>
			<div class="finance-engine-progress-track">${boxes}</div>
			<div class="finance-balance-label">Progress: ${active.progress_boxes}/${active.total_boxes} boxes</div>
			<div class="finance-engine-negotiation-meta">
				<div>
					<span class="finance-balance-label">Annual Value</span>
					<div>$${Math.abs(active.annual_value || 0).toLocaleString()}</div>
				</div>
				<div>
					<span class="finance-balance-label">Contract Length</span>
					<div>${active.contract_length} year(s)</div>
				</div>
			</div>
			<div class="finance-engine-negotiation-staff">
				<label for="finance-title-sponsor-negotiation-staff">Commercial Staff Assigned</label>
				<div class="finance-engine-negotiation-staff-row">
					<input id="finance-title-sponsor-negotiation-staff" type="number" min="0" max="${data.commercial_staff_total || 0}" value="${active.assigned_staff}">
					<button id="finance-title-sponsor-negotiation-apply-staff" class="btn-secondary">Update Staff</button>
				</div>
			</div>
			<div class="finance-engine-negotiation-tiers">
				<button id="finance-title-sponsor-negotiation-sign-btn" class="btn-primary" ${active.ready_to_sign ? '' : 'disabled'}>
					Sign Deal ($${Math.abs(active.annual_value || 0).toLocaleString()})
				</button>
			</div>
		</div>
	`;
}

export function renderEngineNegotiationDetail(data = {}) {
	const active = data.active_negotiation;
	if (data.blocked_reason) {
		return renderNegotiationBlockedState(data.blocked_reason);
	}
	if (!active) {
		return renderNegotiationIdleState({
			intro: 'Select a supplier on the left to open talks. Commercial manager skill and assigned commercial staff will drive progress after each race.',
			commercialManager: data.commercial_manager,
			commercialStaffTotal: data.commercial_staff_total,
		});
	}

	const boxes = Array.from({ length: active.total_boxes }, (_, index) => {
		const boxNumber = index + 1;
		const marker = boxNumber === active.customer_threshold
			? 'C'
			: boxNumber === active.partner_threshold
				? 'P'
				: boxNumber === active.works_threshold
					? 'W'
					: '';
		return `
			<div class="finance-engine-progress-box ${boxNumber <= active.progress_boxes ? 'filled' : ''}">
				<span>${marker}</span>
			</div>
		`;
	}).join('');

	const tierButtons = ['customer', 'partner', 'works']
		.filter((tier) => active.available_tiers.includes(tier))
		.map((tier) => {
			const unlocked = active.unlocked_tiers.includes(tier);
			const value = active.annual_values?.[tier] || 0;
			const sign = value < 0 ? '+' : '-';
			return `
				<button class="btn-primary finance-engine-tier-btn" data-engine-tier="${tier}" ${unlocked ? '' : 'disabled'}>
					Sign ${tier[0].toUpperCase()}${tier.slice(1)} (${sign}$${Math.abs(value).toLocaleString()})
				</button>
			`;
		}).join('');

	return `
		<div class="finance-engine-negotiation-card">
			<div class="finance-balance-label">Active Negotiation</div>
			<h3>${active.supplier_name}</h3>
			<div class="finance-engine-progress-track">${boxes}</div>
			<div class="finance-balance-label">Progress: ${active.progress_boxes}/${active.total_boxes} boxes</div>
			<div class="finance-engine-negotiation-meta">
				<div>
					<span class="finance-balance-label">Contract Length</span>
					<div>${active.contract_length} year(s)</div>
				</div>
				<div>
					<span class="finance-balance-label">Unlocked</span>
					<div>${active.unlocked_tiers.map((tier) => tier[0].toUpperCase() + tier.slice(1)).join(', ') || 'None yet'}</div>
				</div>
			</div>
			<div class="finance-engine-negotiation-staff">
				<label for="finance-engine-negotiation-staff">Commercial Staff Assigned</label>
				<div class="finance-engine-negotiation-staff-row">
					<input id="finance-engine-negotiation-staff" type="number" min="0" max="${data.commercial_staff_total || 0}" value="${active.assigned_staff}">
					<button id="finance-engine-negotiation-apply-staff" class="btn-secondary">Update Staff</button>
				</div>
			</div>
			<div class="finance-engine-negotiation-tiers">${tierButtons}</div>
		</div>
	`;
}

export { formatMoney };
