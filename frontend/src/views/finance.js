/**
 * Finance View
 * Displays team balance, commercial deals, suppliers, and ledger data.
 */

export default class FinanceView {
	constructor() {
		this.tabBtns = document.querySelectorAll('.finance-tab-btn');
		this.panels = {
			overview: document.getElementById('finance-content-overview'),
			commercial: document.getElementById('finance-content-commercial'),
			suppliers: document.getElementById('finance-content-suppliers'),
			ledger: document.getElementById('finance-content-ledger'),
		};
		this.balanceEl = document.getElementById('finance-balance-value');
		this.netPlEl = document.getElementById('finance-net-pl');
		this.projectedBalanceEl = document.getElementById('finance-projected-balance');
		this.nextRaceNetEl = document.getElementById('finance-next-race-net');
		this.nextRaceIncomeEl = document.getElementById('finance-next-race-income');
		this.nextRaceOutgoingsEl = document.getElementById('finance-next-race-outgoings');
		this.prizeEntitlementEl = document.getElementById('finance-prize-entitlement');
		this.prizePaidEl = document.getElementById('finance-prize-paid');
		this.prizeRemainingEl = document.getElementById('finance-prize-remaining');
		this.prizeProgressEl = document.getElementById('finance-prize-progress');
		this.prizeOutlookEl = document.getElementById('finance-prize-outlook');
		this.facilitiesStatusEl = document.getElementById('finance-facilities-status');
		this.contractAlertsEl = document.getElementById('finance-contract-alerts');
		this.incomeTotalEl = document.getElementById('finance-income-total');
		this.expenseTotalEl = document.getElementById('finance-expense-total');
		this.transportTotalEl = document.getElementById('finance-transport-total');
		this.testingTotalEl = document.getElementById('finance-testing-total');
		this.workforceTotalEl = document.getElementById('finance-workforce-total');
		this.engineSupplierTotalEl = document.getElementById('finance-engine-supplier-total');
		this.tyreSupplierTotalEl = document.getElementById('finance-tyre-supplier-total');
		this.fuelSupplierTotalEl = document.getElementById('finance-fuel-supplier-total');
		this.sponsorshipTotalEl = document.getElementById('finance-sponsorship-total');
		this.sponsorNameEl = document.getElementById('finance-sponsor-name');
		this.sponsorReplaceBtn = document.getElementById('finance-sponsor-replace-btn');
		this.engineSupplierReplaceBtn = document.getElementById('finance-engine-supplier-replace-btn');
		this.tyreSupplierReplaceBtn = document.getElementById('finance-tyre-supplier-replace-btn');
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
		this.fuelSupplierNameEl = document.getElementById('finance-fuel-supplier-name');
		this.fuelSupplierDealEl = document.getElementById('finance-fuel-supplier-deal');
		this.fuelSupplierAnnualEl = document.getElementById('finance-fuel-supplier-annual');
		this.fuelSupplierInstallmentEl = document.getElementById('finance-fuel-supplier-installment');
		this.fuelSupplierPaidEl = document.getElementById('finance-fuel-supplier-paid');
		this.fuelSupplierRemainingEl = document.getElementById('finance-fuel-supplier-remaining');
		this.fuelSupplierLogoWrap = document.getElementById('finance-fuel-supplier-logo-wrap');
		this.trackPlBody = document.getElementById('finance-track-pl-body');
		this.tbody = document.getElementById('finance-transactions-body');
		this.onReplaceTitleSponsor = null;
		this.onReplaceEngineSupplier = null;
		this.onReplaceTyreSupplier = null;
		this.bindTabs();
		this.bindSponsorActions();
	}

	setReplaceTitleSponsorHandler(handler) {
		this.onReplaceTitleSponsor = handler;
	}

	setReplaceTyreSupplierHandler(handler) {
		this.onReplaceTyreSupplier = handler;
	}

	setReplaceEngineSupplierHandler(handler) {
		this.onReplaceEngineSupplier = handler;
	}

	formatMoney(value, { signed = false } = {}) {
		const amount = Number(value || 0);
		const formatted = `$${Math.abs(amount).toLocaleString()}`;
		if (!signed) {
			return amount < 0 ? `-${formatted}` : formatted;
		}
		return amount >= 0 ? `+${formatted}` : `-${formatted}`;
	}

	applyMoneyState(element, value, { signed = false } = {}) {
		if (!element) return;
		element.textContent = this.formatMoney(value, { signed });
		const amount = Number(value || 0);
		element.className = amount < 0
			? 'finance-balance-amount finance-negative'
			: 'finance-balance-amount';
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
		const showPanel = (panel) => {
			if (!panel) return;
			panel.style.display = 'block';
			panel.classList.remove('finance-tab-enter');
			void panel.offsetWidth;
			panel.classList.add('finance-tab-enter');
		};
		this.tabBtns.forEach((btn) => {
			btn.addEventListener('click', () => {
				this.tabBtns.forEach((b) => b.classList.remove('active'));
				btn.classList.add('active');
				Object.values(this.panels).forEach((panel) => {
					if (panel) panel.style.display = 'none';
				});
				showPanel(this.panels[btn.getAttribute('data-type')]);
			});
		});
	}

	bindSponsorActions() {
		if (this.sponsorReplaceBtn) {
			this.sponsorReplaceBtn.addEventListener('click', () => {
				if (!this.onReplaceTitleSponsor) return;
				const sponsorName = this.sponsorReplaceBtn.getAttribute('data-sponsor-name');
				if (!sponsorName) return;
				this.onReplaceTitleSponsor(sponsorName);
			});
		}
		if (this.engineSupplierReplaceBtn) {
			this.engineSupplierReplaceBtn.addEventListener('click', () => {
				if (!this.onReplaceEngineSupplier) return;
				const supplierName = this.engineSupplierReplaceBtn.getAttribute('data-supplier-name');
				if (!supplierName) return;
				this.onReplaceEngineSupplier(supplierName);
			});
		}
		if (this.tyreSupplierReplaceBtn) {
			this.tyreSupplierReplaceBtn.addEventListener('click', () => {
				if (!this.onReplaceTyreSupplier) return;
				const supplierName = this.tyreSupplierReplaceBtn.getAttribute('data-supplier-name');
				if (!supplierName) return;
				this.onReplaceTyreSupplier(supplierName);
			});
		}
	}

	renderOverview(overview = {}, summary = {}, prizeMeta = {}) {
		this.applyMoneyState(this.balanceEl, prizeMeta.balance || 0);
		this.applyMoneyState(this.netPlEl, summary.net_profit_loss || 0);
		this.applyMoneyState(this.projectedBalanceEl, overview.projected_end_balance || 0);
		this.applyMoneyState(this.nextRaceNetEl, overview.next_race_net || 0);
		if (this.nextRaceIncomeEl) this.nextRaceIncomeEl.textContent = this.formatMoney(overview.next_race_income || 0);
		if (this.nextRaceOutgoingsEl) this.nextRaceOutgoingsEl.textContent = this.formatMoney(-(overview.next_race_outgoings || 0));
		if (this.prizeEntitlementEl) this.prizeEntitlementEl.textContent = this.formatMoney(prizeMeta.entitlement || 0);
		if (this.prizePaidEl) this.prizePaidEl.textContent = this.formatMoney(prizeMeta.paid || 0);
		if (this.prizeRemainingEl) this.prizeRemainingEl.textContent = this.formatMoney(prizeMeta.remaining || 0);
		if (this.prizeProgressEl) this.prizeProgressEl.textContent = `Race installments: ${prizeMeta.racesPaid || 0} / ${prizeMeta.totalRaces || 0}`;
		if (this.prizeOutlookEl) this.prizeOutlookEl.textContent = overview.prize_outlook || '-';
		if (this.facilitiesStatusEl) this.facilitiesStatusEl.textContent = overview.facilities_status || '-';
		if (this.incomeTotalEl) this.incomeTotalEl.textContent = this.formatMoney(summary.income_total || 0);
		if (this.expenseTotalEl) this.expenseTotalEl.textContent = this.formatMoney(summary.expense_total || 0);
		if (this.transportTotalEl) this.transportTotalEl.textContent = this.formatMoney(summary.transport_total || 0);
		if (this.testingTotalEl) this.testingTotalEl.textContent = this.formatMoney(summary.testing_total || 0);
		if (this.workforceTotalEl) this.workforceTotalEl.textContent = this.formatMoney(summary.workforce_total || 0);
		if (this.engineSupplierTotalEl) this.engineSupplierTotalEl.textContent = this.formatMoney(summary.engine_supplier_total || 0);
		if (this.tyreSupplierTotalEl) this.tyreSupplierTotalEl.textContent = this.formatMoney(summary.tyre_supplier_total || 0);
		if (this.fuelSupplierTotalEl) this.fuelSupplierTotalEl.textContent = this.formatMoney(summary.fuel_supplier_total || 0, { signed: true });
		if (this.sponsorshipTotalEl) this.sponsorshipTotalEl.textContent = this.formatMoney(summary.sponsorship_total || 0);

		if (this.contractAlertsEl) {
			const alerts = Array.isArray(overview.contract_alerts) ? overview.contract_alerts : [];
			this.contractAlertsEl.innerHTML = alerts.length
				? alerts.map((alert) => `<li class="finance-alert-item">${alert}</li>`).join('')
				: '<li class="finance-alert-item">No immediate contract risks.</li>';
		}
	}

	renderCommercial(data) {
		const sponsor = data.sponsor || {};
		const sponsorName = sponsor.name || 'Unassigned';
		const sponsorContractLength = sponsor.contract_length || 0;
		const sponsorPendingReplacement = Boolean(sponsor.pending_replacement);

		if (this.sponsorNameEl) this.sponsorNameEl.textContent = sponsorName;
		if (this.sponsorReplaceBtn) {
			const canReplace = Boolean(sponsor.name) && sponsorContractLength < 2 && !sponsorPendingReplacement;
			this.sponsorReplaceBtn.disabled = !canReplace;
			if (canReplace) {
				this.sponsorReplaceBtn.setAttribute('data-sponsor-name', sponsor.name);
			} else {
				this.sponsorReplaceBtn.removeAttribute('data-sponsor-name');
			}
		}
		if (this.sponsorAnnualEl) this.sponsorAnnualEl.textContent = this.formatMoney(sponsor.annual_value || 0);
		if (this.sponsorInstallmentEl) this.sponsorInstallmentEl.textContent = this.formatMoney(sponsor.installment || 0);
		if (this.sponsorPaidEl) this.sponsorPaidEl.textContent = this.formatMoney(sponsor.paid_so_far || 0);
		if (this.sponsorRemainingEl) this.sponsorRemainingEl.textContent = this.formatMoney(sponsor.remaining || 0);
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
		if (this.otherSponsorshipNameEl) this.otherSponsorshipNameEl.textContent = 'Minor Sponsors';
		if (this.otherSponsorshipAnnualEl) this.otherSponsorshipAnnualEl.textContent = this.formatMoney(otherSponsorship.annual_value || 0);
		if (this.otherSponsorshipInstallmentEl) this.otherSponsorshipInstallmentEl.textContent = this.formatMoney(otherSponsorship.installment || 0);
		if (this.otherSponsorshipPaidEl) this.otherSponsorshipPaidEl.textContent = this.formatMoney(otherSponsorship.paid_so_far || 0);
		if (this.otherSponsorshipRemainingEl) this.otherSponsorshipRemainingEl.textContent = this.formatMoney(otherSponsorship.remaining || 0);
		if (this.otherSponsorshipLogoWrap) this.otherSponsorshipLogoWrap.innerHTML = '';
	}

	renderSuppliers(data) {
		const engineSupplier = data.engine_supplier || {};
		const engineSupplierName = engineSupplier.name || 'Unassigned';
		const engineSupplierContractLength = engineSupplier.contract_length || 0;
		const engineSupplierPendingReplacement = Boolean(engineSupplier.pending_replacement);
		const engineSupplierBuildsOwnEngine = Boolean(engineSupplier.builds_own_engine);

		if (this.engineSupplierNameEl) this.engineSupplierNameEl.textContent = engineSupplierName;
		if (this.engineSupplierReplaceBtn) {
			const canReplace = Boolean(engineSupplier.name) && !engineSupplierBuildsOwnEngine && engineSupplierContractLength < 2 && !engineSupplierPendingReplacement;
			this.engineSupplierReplaceBtn.disabled = !canReplace;
			if (canReplace) {
				this.engineSupplierReplaceBtn.setAttribute('data-supplier-name', engineSupplier.name);
			} else {
				this.engineSupplierReplaceBtn.removeAttribute('data-supplier-name');
			}
		}
		if (this.engineSupplierDealEl) this.engineSupplierDealEl.textContent = engineSupplier.deal || '-';
		if (this.engineSupplierAnnualEl) this.engineSupplierAnnualEl.textContent = this.formatMoney(engineSupplier.annual_value || 0);
		if (this.engineSupplierInstallmentEl) this.engineSupplierInstallmentEl.textContent = this.formatMoney(engineSupplier.installment || 0);
		if (this.engineSupplierPaidEl) this.engineSupplierPaidEl.textContent = this.formatMoney(engineSupplier.paid_so_far || 0);
		if (this.engineSupplierRemainingEl) this.engineSupplierRemainingEl.textContent = this.formatMoney(engineSupplier.remaining || 0);
		this.setSupplierLogo(this.engineSupplierLogoWrap, engineSupplier.name);

		const tyreSupplier = data.tyre_supplier || {};
		const tyreSupplierName = tyreSupplier.name || 'Unassigned';
		const tyreSupplierContractLength = tyreSupplier.contract_length || 0;
		const tyreSupplierPendingReplacement = Boolean(tyreSupplier.pending_replacement);

		if (this.tyreSupplierNameEl) this.tyreSupplierNameEl.textContent = tyreSupplierName;
		if (this.tyreSupplierReplaceBtn) {
			const canReplace = Boolean(tyreSupplier.name) && tyreSupplierContractLength < 2 && !tyreSupplierPendingReplacement;
			this.tyreSupplierReplaceBtn.disabled = !canReplace;
			if (canReplace) {
				this.tyreSupplierReplaceBtn.setAttribute('data-supplier-name', tyreSupplier.name);
			} else {
				this.tyreSupplierReplaceBtn.removeAttribute('data-supplier-name');
			}
		}
		if (this.tyreSupplierDealEl) this.tyreSupplierDealEl.textContent = tyreSupplier.deal || '-';
		if (this.tyreSupplierAnnualEl) this.tyreSupplierAnnualEl.textContent = this.formatMoney(tyreSupplier.annual_value || 0);
		if (this.tyreSupplierInstallmentEl) this.tyreSupplierInstallmentEl.textContent = this.formatMoney(tyreSupplier.installment || 0);
		if (this.tyreSupplierPaidEl) this.tyreSupplierPaidEl.textContent = this.formatMoney(tyreSupplier.paid_so_far || 0);
		if (this.tyreSupplierRemainingEl) this.tyreSupplierRemainingEl.textContent = this.formatMoney(tyreSupplier.remaining || 0);
		this.setSupplierLogo(this.tyreSupplierLogoWrap, tyreSupplier.name);

		const fuelSupplier = data.fuel_supplier || {};
		const annualSign = (fuelSupplier.annual_value || 0) < 0 ? '+' : '-';
		const installmentSign = fuelSupplier.direction === 'income' ? '+' : '-';
		if (this.fuelSupplierNameEl) this.fuelSupplierNameEl.textContent = fuelSupplier.name || 'Unassigned';
		if (this.fuelSupplierDealEl) this.fuelSupplierDealEl.textContent = fuelSupplier.deal || '-';
		if (this.fuelSupplierAnnualEl) this.fuelSupplierAnnualEl.textContent = `${annualSign}$${Math.abs(fuelSupplier.annual_value || 0).toLocaleString()}`;
		if (this.fuelSupplierInstallmentEl) this.fuelSupplierInstallmentEl.textContent = `${installmentSign}$${Math.abs(fuelSupplier.installment || 0).toLocaleString()}`;
		if (this.fuelSupplierPaidEl) this.fuelSupplierPaidEl.textContent = this.formatMoney(fuelSupplier.paid_so_far || 0);
		if (this.fuelSupplierRemainingEl) this.fuelSupplierRemainingEl.textContent = this.formatMoney(fuelSupplier.remaining || 0);
		this.setSupplierLogo(this.fuelSupplierLogoWrap, fuelSupplier.name);
	}

	renderLedger(data) {
		if (this.trackPlBody) {
			this.trackPlBody.innerHTML = '';
			const trackRows = data.track_profit_loss || [];
			trackRows.forEach((rowData) => {
				const row = document.createElement('tr');
				const netClass = rowData.net >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
				row.innerHTML = `
					<td>${rowData.track}</td>
					<td>${rowData.type || '-'}</td>
					<td>${rowData.country}</td>
					<td class="finance-amount-positive">$${(rowData.income || 0).toLocaleString()}</td>
					<td class="finance-amount-negative">$${(rowData.expense || 0).toLocaleString()}</td>
					<td class="${netClass}">${rowData.net >= 0 ? '+' : '-'}$${Math.abs(rowData.net || 0).toLocaleString()}</td>
				`;
				this.trackPlBody.appendChild(row);
			});
			if (trackRows.length === 0) {
				this.trackPlBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b;">No track-linked finance yet.</td></tr>';
			}
		}

		if (this.tbody) {
			this.tbody.innerHTML = '';
			const transactions = data.transactions || [];
			const reversed = [...transactions].reverse();
			reversed.forEach((t) => {
				const row = document.createElement('tr');
				const amountFormatted = '$' + Math.abs(t.amount).toLocaleString();
				const amountClass = t.amount >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
				const amountDisplay = t.amount >= 0 ? '+' + amountFormatted : '-' + amountFormatted;
				const categoryLabel = t.category.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
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

	render(data) {
		const summary = data.summary || {};
		const overview = data.overview || {};
		this.renderOverview(overview, summary, {
			balance: data.balance || 0,
			entitlement: data.prize_money_entitlement || 0,
			paid: data.prize_money_paid || 0,
			remaining: data.prize_money_remaining || 0,
			racesPaid: data.prize_money_races_paid || 0,
			totalRaces: data.prize_money_total_races || 0,
		});
		this.renderCommercial(data);
		this.renderSuppliers(data);
		this.renderLedger(data);
	}
}
