/**
 * Finance View
 * Displays team balance and transaction log.
 */

export default class FinanceView {
	constructor() {
		this.tabBtns = document.querySelectorAll('.finance-tab-btn');
		this.mainContent = document.getElementById('finance-content-main');
		this.trackerContent = document.getElementById('finance-content-tracker');
		this.logContent = document.getElementById('finance-content-log');
		this.balanceEl = document.getElementById('finance-balance-value');
		this.prizeEntitlementEl = document.getElementById('finance-prize-entitlement');
		this.prizePaidEl = document.getElementById('finance-prize-paid');
		this.prizeRemainingEl = document.getElementById('finance-prize-remaining');
		this.incomeTotalEl = document.getElementById('finance-income-total');
		this.expenseTotalEl = document.getElementById('finance-expense-total');
		this.netPlEl = document.getElementById('finance-net-pl');
		this.transportTotalEl = document.getElementById('finance-transport-total');
		this.workforceTotalEl = document.getElementById('finance-workforce-total');
		this.engineSupplierTotalEl = document.getElementById('finance-engine-supplier-total');
		this.tyreSupplierTotalEl = document.getElementById('finance-tyre-supplier-total');
		this.sponsorshipTotalEl = document.getElementById('finance-sponsorship-total');
		this.prizeProgressEl = document.getElementById('finance-prize-progress');
		this.sponsorNameEl = document.getElementById('finance-sponsor-name');
		this.sponsorAnnualEl = document.getElementById('finance-sponsor-annual');
		this.sponsorInstallmentEl = document.getElementById('finance-sponsor-installment');
		this.sponsorPaidEl = document.getElementById('finance-sponsor-paid');
		this.sponsorRemainingEl = document.getElementById('finance-sponsor-remaining');
		this.sponsorLogoWrap = document.getElementById('finance-sponsor-logo-wrap');
		this.otherSponsorshipNameEl = document.getElementById('finance-other-sponsorship-name');
		this.otherSponsorshipAnnualEl = document.getElementById('finance-other-sponsorship-annual');
		this.otherSponsorshipInstallmentEl = document.getElementById('finance-other-sponsorship-installment');
		this.otherSponsorshipPaidEl = document.getElementById('finance-other-sponsorship-paid');
		this.otherSponsorshipRemainingEl = document.getElementById('finance-other-sponsorship-remaining');
		this.otherSponsorshipLogoWrap = document.getElementById('finance-other-sponsorship-logo-wrap');
		this.engineSupplierNameEl = document.getElementById('finance-engine-supplier-name');
		this.engineSupplierDealEl = document.getElementById('finance-engine-supplier-deal');
		this.engineSupplierAnnualEl = document.getElementById('finance-engine-supplier-annual');
		this.engineSupplierInstallmentEl = document.getElementById('finance-engine-supplier-installment');
		this.engineSupplierPaidEl = document.getElementById('finance-engine-supplier-paid');
		this.engineSupplierRemainingEl = document.getElementById('finance-engine-supplier-remaining');
		this.engineSupplierLogoWrap = document.getElementById('finance-engine-supplier-logo-wrap');
		this.tyreSupplierNameEl = document.getElementById('finance-tyre-supplier-name');
		this.tyreSupplierDealEl = document.getElementById('finance-tyre-supplier-deal');
		this.tyreSupplierAnnualEl = document.getElementById('finance-tyre-supplier-annual');
		this.tyreSupplierInstallmentEl = document.getElementById('finance-tyre-supplier-installment');
		this.tyreSupplierPaidEl = document.getElementById('finance-tyre-supplier-paid');
		this.tyreSupplierRemainingEl = document.getElementById('finance-tyre-supplier-remaining');
		this.tyreSupplierLogoWrap = document.getElementById('finance-tyre-supplier-logo-wrap');
		this.trackPlBody = document.getElementById('finance-track-pl-body');
		this.tbody = document.getElementById('finance-transactions-body');
		this.bindTabs();
	}

	setSupplierLogo(targetWrap, supplierName) {
		if (!targetWrap) return;
		if (!supplierName) {
			targetWrap.innerHTML = '';
			return;
		}
		const slug = supplierName.toLowerCase().replace(/\s+/g, '-');
		const fileNameBySlug = {
			hartek: 'harteck',
		};
		const preferred = fileNameBySlug[slug] || slug;
		const fallback = `${slug}.png`;
		targetWrap.innerHTML = `
			<img class="supplier-logo" src="assets/supplier_logos/${preferred}.png" alt="${supplierName} logo"
				onerror="if(!this.dataset.f1){this.dataset.f1='1';this.src='assets/supplier_logos/${fallback}';}else{this.style.display='none';}">
		`;
	}

	bindTabs() {
		if (!this.tabBtns.length) return;
		const panelByType = {
			main: this.mainContent,
			tracker: this.trackerContent,
			log: this.logContent,
		};
		const showPanel = (panel) => {
			if (!panel) return;
			panel.style.display = 'block';
			panel.classList.remove('finance-tab-enter');
			// Force reflow so the animation can replay on repeated tab changes.
			void panel.offsetWidth;
			panel.classList.add('finance-tab-enter');
		};
		this.tabBtns.forEach((btn) => {
			btn.addEventListener('click', () => {
				this.tabBtns.forEach((b) => b.classList.remove('active'));
				btn.classList.add('active');
				const type = btn.getAttribute('data-type');
				if (this.mainContent) this.mainContent.style.display = 'none';
				if (this.trackerContent) this.trackerContent.style.display = 'none';
				if (this.logContent) this.logContent.style.display = 'none';
				showPanel(panelByType[type]);
			});
		});
	}

	render(data) {
		// Update balance display
		const balance = data.balance || 0;
		const formatted = '$' + Math.abs(balance).toLocaleString();
		this.balanceEl.textContent = balance < 0 ? '-' + formatted : formatted;
		this.balanceEl.className = balance < 0
			? 'finance-balance-amount finance-negative'
			: 'finance-balance-amount';

		const entitlement = data.prize_money_entitlement || 0;
		const paid = data.prize_money_paid || 0;
		const remaining = data.prize_money_remaining || 0;
		const racesPaid = data.prize_money_races_paid || 0;
		const totalRaces = data.prize_money_total_races || 0;

		if (this.prizeEntitlementEl) this.prizeEntitlementEl.textContent = '$' + entitlement.toLocaleString();
		if (this.prizePaidEl) this.prizePaidEl.textContent = '$' + paid.toLocaleString();
		if (this.prizeRemainingEl) this.prizeRemainingEl.textContent = '$' + remaining.toLocaleString();
		if (this.prizeProgressEl) this.prizeProgressEl.textContent = `Race installments: ${racesPaid} / ${totalRaces}`;

		const summary = data.summary || {};
		const incomeTotal = summary.income_total || 0;
		const expenseTotal = summary.expense_total || 0;
		const netPl = summary.net_profit_loss || 0;
		const transportTotal = summary.transport_total || 0;
		const workforceTotal = summary.workforce_total || 0;
		const sponsorshipTotal = summary.sponsorship_total || 0;
		const engineSupplierTotal = summary.engine_supplier_total || 0;
		const tyreSupplierTotal = summary.tyre_supplier_total || 0;

		if (this.incomeTotalEl) this.incomeTotalEl.textContent = '$' + incomeTotal.toLocaleString();
		if (this.expenseTotalEl) this.expenseTotalEl.textContent = '$' + expenseTotal.toLocaleString();
		if (this.transportTotalEl) this.transportTotalEl.textContent = '$' + transportTotal.toLocaleString();
		if (this.workforceTotalEl) this.workforceTotalEl.textContent = '$' + workforceTotal.toLocaleString();
		if (this.engineSupplierTotalEl) this.engineSupplierTotalEl.textContent = '$' + engineSupplierTotal.toLocaleString();
		if (this.tyreSupplierTotalEl) this.tyreSupplierTotalEl.textContent = '$' + tyreSupplierTotal.toLocaleString();
		if (this.sponsorshipTotalEl) this.sponsorshipTotalEl.textContent = '$' + sponsorshipTotal.toLocaleString();
		if (this.netPlEl) {
			const netFormatted = '$' + Math.abs(netPl).toLocaleString();
			this.netPlEl.textContent = netPl < 0 ? '-' + netFormatted : netFormatted;
			this.netPlEl.className = netPl < 0
				? 'finance-balance-amount finance-negative'
				: 'finance-balance-amount';
		}

		const sponsor = data.sponsor || {};
		const sponsorName = sponsor.name || 'Unassigned';
		const annualValue = sponsor.annual_value || 0;
		const installment = sponsor.installment || 0;
		const paidSoFar = sponsor.paid_so_far || 0;
		const sponsorRemaining = sponsor.remaining || 0;

		if (this.sponsorNameEl) this.sponsorNameEl.textContent = sponsorName;
		if (this.sponsorAnnualEl) this.sponsorAnnualEl.textContent = '$' + annualValue.toLocaleString();
		if (this.sponsorInstallmentEl) this.sponsorInstallmentEl.textContent = '$' + installment.toLocaleString();
		if (this.sponsorPaidEl) this.sponsorPaidEl.textContent = '$' + paidSoFar.toLocaleString();
		if (this.sponsorRemainingEl) this.sponsorRemainingEl.textContent = '$' + sponsorRemaining.toLocaleString();
		if (this.sponsorLogoWrap) {
			if (!sponsor.name) {
				this.sponsorLogoWrap.innerHTML = '';
			} else {
				const encodedOriginal = encodeURIComponent(sponsor.name);
				const encodedLower = encodeURIComponent(sponsor.name.toLowerCase());
				const encodedUpper = encodeURIComponent(sponsor.name.toUpperCase());
				this.sponsorLogoWrap.innerHTML = `
					<img class="sponsor-logo" src="assets/sponsor_logos/${encodedOriginal}.png" alt="${sponsor.name} logo"
						onerror="if(!this.dataset.f1){this.dataset.f1='1';this.src='assets/sponsor_logos/${encodedLower}.png';}else if(!this.dataset.f2){this.dataset.f2='1';this.src='assets/sponsor_logos/${encodedUpper}.png';}else{this.style.display='none';}">
				`;
			}
		}

		const otherSponsorship = data.other_sponsorship || {};
		const otherAnnual = otherSponsorship.annual_value || 0;
		const otherInstallment = otherSponsorship.installment || 0;
		const otherPaid = otherSponsorship.paid_so_far || 0;
		const otherRemaining = otherSponsorship.remaining || 0;

		if (this.otherSponsorshipNameEl) this.otherSponsorshipNameEl.textContent = 'Minor Sponsors';
		if (this.otherSponsorshipAnnualEl) this.otherSponsorshipAnnualEl.textContent = '$' + otherAnnual.toLocaleString();
		if (this.otherSponsorshipInstallmentEl) this.otherSponsorshipInstallmentEl.textContent = '$' + otherInstallment.toLocaleString();
		if (this.otherSponsorshipPaidEl) this.otherSponsorshipPaidEl.textContent = '$' + otherPaid.toLocaleString();
		if (this.otherSponsorshipRemainingEl) this.otherSponsorshipRemainingEl.textContent = '$' + otherRemaining.toLocaleString();
		if (this.otherSponsorshipLogoWrap) this.otherSponsorshipLogoWrap.innerHTML = '';

		const engineSupplier = data.engine_supplier || {};
		const engineSupplierName = engineSupplier.name || 'Unassigned';
		const engineSupplierDeal = engineSupplier.deal || '-';
		const engineSupplierAnnual = engineSupplier.annual_value || 0;
		const engineSupplierInstallment = engineSupplier.installment || 0;
		const engineSupplierPaid = engineSupplier.paid_so_far || 0;
		const engineSupplierRemaining = engineSupplier.remaining || 0;

		if (this.engineSupplierNameEl) this.engineSupplierNameEl.textContent = engineSupplierName;
		if (this.engineSupplierDealEl) this.engineSupplierDealEl.textContent = engineSupplierDeal;
		if (this.engineSupplierAnnualEl) this.engineSupplierAnnualEl.textContent = '$' + engineSupplierAnnual.toLocaleString();
		if (this.engineSupplierInstallmentEl) this.engineSupplierInstallmentEl.textContent = '$' + engineSupplierInstallment.toLocaleString();
		if (this.engineSupplierPaidEl) this.engineSupplierPaidEl.textContent = '$' + engineSupplierPaid.toLocaleString();
		if (this.engineSupplierRemainingEl) this.engineSupplierRemainingEl.textContent = '$' + engineSupplierRemaining.toLocaleString();
		this.setSupplierLogo(this.engineSupplierLogoWrap, engineSupplier.name);

		const tyreSupplier = data.tyre_supplier || {};
		const tyreSupplierName = tyreSupplier.name || 'Unassigned';
		const tyreSupplierDeal = tyreSupplier.deal || '-';
		const tyreSupplierAnnual = tyreSupplier.annual_value || 0;
		const tyreSupplierInstallment = tyreSupplier.installment || 0;
		const tyreSupplierPaid = tyreSupplier.paid_so_far || 0;
		const tyreSupplierRemaining = tyreSupplier.remaining || 0;

		if (this.tyreSupplierNameEl) this.tyreSupplierNameEl.textContent = tyreSupplierName;
		if (this.tyreSupplierDealEl) this.tyreSupplierDealEl.textContent = tyreSupplierDeal;
		if (this.tyreSupplierAnnualEl) this.tyreSupplierAnnualEl.textContent = '$' + tyreSupplierAnnual.toLocaleString();
		if (this.tyreSupplierInstallmentEl) this.tyreSupplierInstallmentEl.textContent = '$' + tyreSupplierInstallment.toLocaleString();
		if (this.tyreSupplierPaidEl) this.tyreSupplierPaidEl.textContent = '$' + tyreSupplierPaid.toLocaleString();
		if (this.tyreSupplierRemainingEl) this.tyreSupplierRemainingEl.textContent = '$' + tyreSupplierRemaining.toLocaleString();
		this.setSupplierLogo(this.tyreSupplierLogoWrap, tyreSupplier.name);

		// Track P/L table
		if (this.trackPlBody) {
			this.trackPlBody.innerHTML = '';
			const trackRows = data.track_profit_loss || [];
			trackRows.forEach(rowData => {
				const row = document.createElement('tr');
				const netClass = rowData.net >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
				row.innerHTML = `
					<td>${rowData.track}</td>
					<td>${rowData.country}</td>
					<td class="finance-amount-positive">$${(rowData.income || 0).toLocaleString()}</td>
					<td class="finance-amount-negative">$${(rowData.expense || 0).toLocaleString()}</td>
					<td class="${netClass}">${rowData.net >= 0 ? '+' : '-'}$${Math.abs(rowData.net || 0).toLocaleString()}</td>
				`;
				this.trackPlBody.appendChild(row);
			});

			if (trackRows.length === 0) {
				this.trackPlBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b;">No track-linked finance yet.</td></tr>';
			}
		}

		// Render transactions (most recent first)
		this.tbody.innerHTML = '';
		const transactions = data.transactions || [];
		const reversed = [...transactions].reverse();

		reversed.forEach(t => {
			const row = document.createElement('tr');
			const amountFormatted = '$' + Math.abs(t.amount).toLocaleString();
			const amountClass = t.amount >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
			const amountDisplay = t.amount >= 0 ? '+' + amountFormatted : '-' + amountFormatted;
			const categoryLabel = t.category.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
			const categoryClass = t.category === 'transport' ? 'finance-category-badge finance-category-transport' : 'finance-category-badge';

			row.innerHTML = `
				<td>Week ${t.week}, ${t.year}</td>
				<td>${t.description}</td>
				<td><span class="${categoryClass}">${categoryLabel}</span></td>
				<td class="${amountClass}">${amountDisplay}</td>
			`;
			this.tbody.appendChild(row);
		});

		if (transactions.length === 0) {
			this.tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b;">No transactions yet.</td></tr>';
		}
	}
}
