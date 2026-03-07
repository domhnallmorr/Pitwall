function renderFinanceSummaryCards() {
	const container = document.getElementById('finance-summary');
	if (!container) return;

	const cards = [
		{ label: 'Team Balance', id: 'finance-balance-value', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Season Prize Money', id: 'finance-prize-entitlement', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Prize Paid', id: 'finance-prize-paid', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Prize Remaining', id: 'finance-prize-remaining', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Season Income', id: 'finance-income-total', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Season Expenses', id: 'finance-expense-total', className: 'finance-balance-amount finance-negative', defaultValue: '$0' },
		{ label: 'Net Profit/Loss', id: 'finance-net-pl', className: 'finance-balance-amount', defaultValue: '$0' },
		{ label: 'Transport Costs', id: 'finance-transport-total', className: 'finance-balance-amount finance-negative', defaultValue: '$0' },
		{ label: 'Workforce Costs', id: 'finance-workforce-total', className: 'finance-balance-amount finance-negative', defaultValue: '$0' },
		{ label: 'Engine Supplier Costs', id: 'finance-engine-supplier-total', className: 'finance-balance-amount finance-negative', defaultValue: '$0' },
		{ label: 'Tyre Supplier Costs', id: 'finance-tyre-supplier-total', className: 'finance-balance-amount finance-negative', defaultValue: '$0' },
		{ label: 'Sponsorship Income', id: 'finance-sponsorship-total', className: 'finance-balance-amount', defaultValue: '$0' },
	];

	container.innerHTML = cards.map((card) => `
		<div class="finance-balance-card">
			<div class="finance-balance-label">${card.label}</div>
			<div id="${card.id}" class="${card.className}">${card.defaultValue}</div>
		</div>
	`).join('');
}

function renderFinanceSupplierSections() {
	const container = document.getElementById('finance-supplier-sections');
	if (!container) return;

	const cards = [
		{
			cardId: 'finance-sponsor-card',
			logoWrapId: 'finance-sponsor-logo-wrap',
			title: 'Title Sponsor',
			nameId: 'finance-sponsor-name',
			nameDefault: 'Unassigned',
			rows: [
				{ label: 'Annual Value', id: 'finance-sponsor-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-sponsor-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-sponsor-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-sponsor-remaining', defaultValue: '$0' },
			],
		},
		{
			cardId: 'finance-engine-supplier-card',
			logoWrapId: 'finance-engine-supplier-logo-wrap',
			title: 'Engine Supplier',
			nameId: 'finance-engine-supplier-name',
			nameDefault: 'Unassigned',
			rows: [
				{ label: 'Deal', id: 'finance-engine-supplier-deal', defaultValue: '-' },
				{ label: 'Annual Cost', id: 'finance-engine-supplier-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-engine-supplier-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-engine-supplier-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-engine-supplier-remaining', defaultValue: '$0' },
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
		{
			cardId: 'finance-tyre-supplier-card',
			logoWrapId: 'finance-tyre-supplier-logo-wrap',
			title: 'Tyre Supplier',
			nameId: 'finance-tyre-supplier-name',
			nameDefault: 'Unassigned',
			rows: [
				{ label: 'Deal', id: 'finance-tyre-supplier-deal', defaultValue: '-' },
				{ label: 'Annual Cost', id: 'finance-tyre-supplier-annual', defaultValue: '$0' },
				{ label: 'Per Race', id: 'finance-tyre-supplier-installment', defaultValue: '$0' },
				{ label: 'Paid So Far', id: 'finance-tyre-supplier-paid', defaultValue: '$0' },
				{ label: 'Remaining', id: 'finance-tyre-supplier-remaining', defaultValue: '$0' },
			],
		},
	];

	container.innerHTML = cards.map((card) => `
		<div class="finance-sponsor-card" id="${card.cardId}">
			<div class="finance-sponsor-header">
				<div id="${card.logoWrapId}"></div>
				<div>
					<div class="finance-balance-label">${card.title}</div>
					<div id="${card.nameId}" class="finance-section-title">${card.nameDefault}</div>
				</div>
			</div>
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

export function renderLayoutPartials() {
	renderFinanceSummaryCards();
	renderFinanceSupplierSections();
}
