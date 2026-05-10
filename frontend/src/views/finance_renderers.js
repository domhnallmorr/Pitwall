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

export function renderTyreNegotiationSupplierList(suppliers = []) {
	if (!suppliers.length) {
		return '<p class="finance-engine-negotiation-empty">No suppliers available.</p>';
	}
	return suppliers.map((supplier) => `
		<div class="finance-engine-supplier-row">
			<div>
				<div class="finance-section-title">${supplier.name}</div>
				<div class="finance-balance-label">${supplier.country} · Resources ${supplier.resources} · Innovation ${supplier.innovation} · Reliability ${supplier.reliability}</div>
			</div>
			<button class="btn-secondary" data-tyre-supplier-id="${supplier.id}" ${supplier.targetable ? '' : 'disabled'}>
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

function renderHospitalityAction(action = {}, buttonId) {
	const cost = Number(action.cost || 0);
	const progressBonus = Number(action.progress_bonus || 0);
	const eventLabel = action.event_name
		? `${action.event_name}${action.event_week ? ` (Week ${action.event_week})` : ''}`
		: 'the next race';
	const helper = action.booked
		? `Hospitality booked for ${eventLabel}. Race-day bonus queued: +${progressBonus.toFixed(1)} boxes.`
		: `Invite to ${eventLabel} for $${cost.toLocaleString()}. Adds +${progressBonus.toFixed(1)} boxes after the race.`;

	return `
		<div class="finance-engine-negotiation-staff">
			<div class="finance-balance-label">Hospitality</div>
			<p class="finance-balance-label">${helper}</p>
			<button id="${buttonId}" class="btn-secondary" ${action.available ? '' : 'disabled'}>
				Invite To Next Race
			</button>
			${action.reason && !action.booked ? `<div class="finance-balance-label" style="margin-top:8px;">${action.reason}</div>` : ''}
		</div>
	`;
}

function renderStaffAssignmentControl({
	inputId,
	assignedStaff = 0,
	commercialStaffTotal = 0,
}) {
	return `
		<div class="finance-engine-negotiation-staff">
			<div class="finance-engine-negotiation-staff-head">
				<label for="${inputId}">Commercial Staff Assigned</label>
				<span class="finance-engine-negotiation-staff-limit">Max ${commercialStaffTotal || 0}</span>
			</div>
			<div class="finance-engine-negotiation-staff-row">
				<div class="finance-engine-negotiation-stepper">
					<button type="button" class="finance-engine-negotiation-step-btn" data-staff-input-id="${inputId}" data-staff-step="-1" aria-label="Decrease assigned commercial staff">-</button>
					<input id="${inputId}" class="finance-engine-negotiation-step-input" type="number" min="0" max="${commercialStaffTotal || 0}" value="${assignedStaff}">
					<button type="button" class="finance-engine-negotiation-step-btn" data-staff-input-id="${inputId}" data-staff-step="1" aria-label="Increase assigned commercial staff">+</button>
				</div>
			</div>
			<div class="finance-engine-negotiation-staff-note">Changes apply immediately.</div>
		</div>
	`;
}

export function renderTitleSponsorNegotiationDetail(data = {}, options = {}) {
	const active = data.active_negotiation;
	const hospitality = data.hospitality || {};
	const {
		staffInputId = 'finance-title-sponsor-negotiation-staff',
		signButtonId = 'finance-title-sponsor-negotiation-sign-btn',
		hospitalityButtonId = 'finance-title-sponsor-hospitality-btn',
	} = options;
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
	const signButtonLabel = active.ready_to_sign
		? `Sign Deal ($${Math.abs(active.annual_value || 0).toLocaleString()})`
		: 'Negotiations Ongoing';

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
			${renderStaffAssignmentControl({
				inputId: staffInputId,
				assignedStaff: active.assigned_staff,
				commercialStaffTotal: data.commercial_staff_total,
			})}
			${renderHospitalityAction(hospitality, hospitalityButtonId)}
			<div class="finance-engine-negotiation-tiers">
				<button id="${signButtonId}" type="button" class="btn-primary" ${active.ready_to_sign ? '' : 'disabled'}>
					${signButtonLabel}
				</button>
			</div>
		</div>
	`;
}

export function renderEngineNegotiationDetail(data = {}, options = {}) {
	const active = data.active_negotiation;
	const hospitality = data.hospitality || {};
	const {
		staffInputId = 'finance-engine-negotiation-staff',
		hospitalityButtonId = 'finance-engine-hospitality-btn',
	} = options;
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
			${renderStaffAssignmentControl({
				inputId: staffInputId,
				assignedStaff: active.assigned_staff,
				commercialStaffTotal: data.commercial_staff_total,
			})}
			${renderHospitalityAction(hospitality, hospitalityButtonId)}
			<div class="finance-engine-negotiation-tiers">${tierButtons}</div>
		</div>
	`;
}

export function renderTyreNegotiationDetail(data = {}, options = {}) {
	const active = data.active_negotiation;
	const hospitality = data.hospitality || {};
	const {
		staffInputId = 'finance-tyre-negotiation-staff',
		hospitalityButtonId = 'finance-tyre-hospitality-btn',
	} = options;
	if (data.blocked_reason) {
		return renderNegotiationBlockedState(data.blocked_reason);
	}
	if (!active) {
		return renderNegotiationIdleState({
			intro: 'Select a tyre supplier on the left to open talks. Commercial manager skill and assigned commercial staff will drive progress after each race.',
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
				<button class="btn-primary finance-engine-tier-btn" data-tyre-tier="${tier}" ${unlocked ? '' : 'disabled'}>
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
			${renderStaffAssignmentControl({
				inputId: staffInputId,
				assignedStaff: active.assigned_staff,
				commercialStaffTotal: data.commercial_staff_total,
			})}
			${renderHospitalityAction(hospitality, hospitalityButtonId)}
			<div class="finance-engine-negotiation-tiers">${tierButtons}</div>
		</div>
	`;
}

export { formatMoney };
