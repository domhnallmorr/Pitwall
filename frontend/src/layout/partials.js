function renderFinanceSummaryCards() {
	const container = document.getElementById('finance-summary');
	if (!container) return;

	const cards = [
		{ label: 'Team Balance', id: 'finance-balance-value', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Season Net', id: 'finance-net-pl', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Projected Finish', id: 'finance-projected-balance', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Next Race Net', id: 'finance-next-race-net', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Prize Remaining', id: 'finance-prize-remaining', className: 'finance-balance-amount', defaultValue: '$0' },
	];

	container.innerHTML = cards.map((card) => `
		<div class="finance-balance-card">
			<div class="finance-balance-label">${card.label}</div>
			<div id="${card.id}" class="${card.className}">${card.defaultValue}</div>
		</div>
	`).join('');
}

function renderFinanceOverviewSections() {
	const income = document.getElementById('finance-overview-income');
	const expenditure = document.getElementById('finance-overview-expenditure');
	const net = document.getElementById('finance-overview-net');
	const alerts = document.getElementById('finance-contract-alerts');
	if (income) {
		const rows = [
				{ label: 'Sponsorship', id: 'finance-sponsorship-total', defaultValue: '$0' },
				{ label: 'Prize Money', id: 'finance-prize-money-total', defaultValue: '$0' },
				{ label: 'Pay Drivers', id: 'finance-pay-driver-total', defaultValue: '$0' },
				{ label: 'Engine Support', id: 'finance-engine-income-total', defaultValue: '$0' },
				{ label: 'Fuel Income', id: 'finance-fuel-income-total', defaultValue: '$0' },
				{ label: 'Total Income', id: 'finance-income-total', defaultValue: '$0', total: true },
		];
		income.innerHTML = rows.map((row) => `
			<div class="finance-overview-row ${row.total ? 'finance-overview-row-total' : ''}">
				<span class="finance-balance-label">${row.label}</span>
				<strong id="${row.id}" class="finance-overview-value">${row.defaultValue}</strong>
			</div>
		`).join('');
	}

	if (expenditure) {
		const items = [
			{ label: 'Driver Payroll', id: 'finance-driver-wages-total', defaultValue: '$0' },
			{ label: 'Management Salaries', id: 'finance-management-salary-total', defaultValue: '$0' },
			{ label: 'Workforce', id: 'finance-workforce-total', defaultValue: '$0' },
			{ label: 'Commercial Staff', id: 'finance-commercial-staff-total', defaultValue: '$0' },
			{ label: 'Factory Overhead', id: 'finance-factory-overhead-total', defaultValue: '$0' },
			{ label: 'Engine Supplier', id: 'finance-engine-supplier-total', defaultValue: '$0' },
			{ label: 'Tyre Supplier', id: 'finance-tyre-supplier-total', defaultValue: '$0' },
			{ label: 'Fuel Supplier', id: 'finance-fuel-expense-total', defaultValue: '$0' },
			{ label: 'Transport', id: 'finance-transport-total', defaultValue: '$0' },
			{ label: 'Crash Damage', id: 'finance-crash-damage-total', defaultValue: '$0' },
			{ label: 'Wear Repairs', id: 'finance-maintenance-total', defaultValue: '$0' },
			{ label: 'Testing', id: 'finance-testing-total', defaultValue: '$0' },
			{ label: 'Facilities', id: 'finance-facilities-total', defaultValue: '$0' },
			{ label: 'Total Expenditure', id: 'finance-expense-total', defaultValue: '$0', total: true },
		];
		expenditure.innerHTML = items.map((item) => `
			<div class="finance-overview-row ${item.total ? 'finance-overview-row-total' : ''}">
				<span class="finance-balance-label">${item.label}</span>
				<div id="${item.id}" class="finance-overview-value">${item.defaultValue}</div>
			</div>
		`).join('');
	}

	if (net) {
		const rows = [
			{ label: 'Season Income', id: 'finance-net-income-total', defaultValue: '$0' },
			{ label: 'Season Expenditure', id: 'finance-net-expense-total', defaultValue: '$0' },
			{ label: 'Net Profit / Loss', id: 'finance-net-pl-breakdown', defaultValue: '$0' },
			{ label: 'Prize Outlook', id: 'finance-prize-outlook', defaultValue: '-' },
			{ label: 'Facilities Status', id: 'finance-facilities-status', defaultValue: '-' },
		];
		net.innerHTML = rows.map((row) => `
			<div class="finance-overview-row ${row.id === 'finance-prize-outlook' || row.id === 'finance-facilities-status' ? 'finance-overview-row-wide' : ''}">
				<span class="finance-balance-label">${row.label}</span>
				<div id="${row.id}" class="${row.id === 'finance-net-pl-breakdown' ? 'finance-overview-value finance-overview-net' : 'finance-overview-copy'}">${row.defaultValue}</div>
			</div>
		`).join('');
	}

	if (alerts) {
		alerts.innerHTML = '<li class="finance-alert-item">No immediate contract risks.</li>';
	}
}

function renderFinanceCardSections(containerId, cards) {
	const container = document.getElementById(containerId);
	if (!container) return;

	container.innerHTML = cards.map((card) => `
		<div class="finance-sponsor-card" id="${card.cardId}">
			<div class="finance-sponsor-header">
				<div id="${card.logoWrapId}"></div>
				<div>
					<div class="finance-balance-label">${card.title}</div>
					<div id="${card.nameId}" class="finance-section-title">${card.nameDefault}</div>
				</div>
			</div>
			${card.actionButtonId ? `<div class="finance-sponsor-actions"><button id="${card.actionButtonId}" class="btn-secondary">${card.actionButtonLabel}</button></div>` : ''}
			<div class="finance-sponsor-grid">
				${card.rows.map((row) => `
					<div>
						<span class="finance-balance-label">${row.label}</span>
						<div id="${row.id}">${row.defaultValue}</div>
					</div>
				`).join('')}
			</div>
		</div>
	`).join('');
}

function renderFinanceCommercialSections() {
	renderFinanceCardSections('finance-commercial-sections', [
		{
			cardId: 'finance-sponsor-card',
			logoWrapId: 'finance-sponsor-logo-wrap',
			title: 'Title Sponsor',
			nameId: 'finance-sponsor-name',
			nameDefault: 'Unassigned',
			actionButtonId: 'finance-sponsor-replace-btn',
			actionButtonLabel: 'Replace',
			rows: [
				{ label: 'Annual Value', id: 'finance-sponsor-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-sponsor-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-sponsor-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-sponsor-remaining', defaultValue: '$0' },
			],
		},
		{
			cardId: 'finance-other-sponsorship-card',
			logoWrapId: 'finance-other-sponsorship-logo-wrap',
			title: 'Other Sponsorship',
			nameId: 'finance-other-sponsorship-name',
			nameDefault: 'Minor Sponsors',
			rows: [
				{ label: 'Annual Value', id: 'finance-other-sponsorship-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-other-sponsorship-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-other-sponsorship-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-other-sponsorship-remaining', defaultValue: '$0' },
			],
		},
	]);
}

function renderFinanceSupplierSections() {
	renderFinanceCardSections('finance-supplier-sections', [
		{
			cardId: 'finance-engine-supplier-card',
			logoWrapId: 'finance-engine-supplier-logo-wrap',
			title: 'Engine Supplier',
			nameId: 'finance-engine-supplier-name',
			nameDefault: 'Unassigned',
			actionButtonId: 'finance-engine-supplier-replace-btn',
			actionButtonLabel: 'Negotiate',
			rows: [
				{ label: 'Deal', id: 'finance-engine-supplier-deal', defaultValue: '-' },
				{ label: 'Annual Net', id: 'finance-engine-supplier-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-engine-supplier-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-engine-supplier-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-engine-supplier-remaining', defaultValue: '$0' },
			],
		},
		{
			cardId: 'finance-tyre-supplier-card',
			logoWrapId: 'finance-tyre-supplier-logo-wrap',
			title: 'Tyre Supplier',
			nameId: 'finance-tyre-supplier-name',
			nameDefault: 'Unassigned',
			actionButtonId: 'finance-tyre-supplier-replace-btn',
			actionButtonLabel: 'Replace',
			rows: [
				{ label: 'Deal', id: 'finance-tyre-supplier-deal', defaultValue: '-' },
				{ label: 'Annual Cost', id: 'finance-tyre-supplier-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-tyre-supplier-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-tyre-supplier-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-tyre-supplier-remaining', defaultValue: '$0' },
			],
		},
		{
			cardId: 'finance-fuel-supplier-card',
			logoWrapId: 'finance-fuel-supplier-logo-wrap',
			title: 'Fuel Supplier',
			nameId: 'finance-fuel-supplier-name',
			nameDefault: 'Unassigned',
			rows: [
				{ label: 'Deal', id: 'finance-fuel-supplier-deal', defaultValue: '-' },
				{ label: 'Annual Net', id: 'finance-fuel-supplier-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-fuel-supplier-installment', defaultValue: '$0' },
				{ label: 'Paid/Received', id: 'finance-fuel-supplier-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-fuel-supplier-remaining', defaultValue: '$0' },
			],
		},
	]);
}

export function renderLayoutPartials() {
	renderFinanceSummaryCards();
	renderFinanceOverviewSections();
	renderFinanceCommercialSections();
	renderFinanceSupplierSections();
}
