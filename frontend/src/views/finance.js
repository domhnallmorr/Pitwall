/**
 * Finance View
 * Displays team balance, commercial deals, suppliers, and ledger data.
 */

import {
	formatMoney,
	renderEngineNegotiationDetail,
	renderEngineNegotiationSupplierList,
	renderTitleSponsorNegotiationDetail,
	renderTitleSponsorNegotiationSupplierList,
	renderTrackProfitLossHtml,
	renderTransactionsHtml,
} from './finance_renderers.js';

const ELEMENT_GROUPS = {
	overview: {
		balanceEl: 'finance-balance-value',
		netPlEl: 'finance-net-pl',
		projectedBalanceEl: 'finance-projected-balance',
		nextRaceNetEl: 'finance-next-race-net',
		prizeRemainingEl: 'finance-prize-remaining',
		prizeProgressEl: 'finance-prize-progress',
		prizeOutlookEl: 'finance-prize-outlook',
		facilitiesStatusEl: 'finance-facilities-status',
		contractAlertsEl: 'finance-contract-alerts',
		incomeTotalEl: 'finance-income-total',
		netIncomeTotalEl: 'finance-net-income-total',
		netExpenseTotalEl: 'finance-net-expense-total',
		netPlBreakdownEl: 'finance-net-pl-breakdown',
		expenseTotalEl: 'finance-expense-total',
		prizeMoneyTotalEl: 'finance-prize-money-total',
		payDriverTotalEl: 'finance-pay-driver-total',
		engineIncomeTotalEl: 'finance-engine-income-total',
		transportTotalEl: 'finance-transport-total',
		crashDamageTotalEl: 'finance-crash-damage-total',
		sparesTotalEl: 'finance-spares-total',
		testingTotalEl: 'finance-testing-total',
		driverWagesTotalEl: 'finance-driver-wages-total',
		managementSalaryTotalEl: 'finance-management-salary-total',
		designStaffTotalEl: 'finance-design-staff-total',
		engineeringStaffTotalEl: 'finance-engineering-staff-total',
		mechanicsStaffTotalEl: 'finance-mechanics-staff-total',
		commercialStaffTotalEl: 'finance-commercial-staff-total',
		hospitalityTotalEl: 'finance-hospitality-total',
		factoryOverheadTotalEl: 'finance-factory-overhead-total',
		engineSupplierTotalEl: 'finance-engine-supplier-total',
		tyreSupplierTotalEl: 'finance-tyre-supplier-total',
		fuelSupplierTotalEl: 'finance-fuel-supplier-total',
		fuelIncomeTotalEl: 'finance-fuel-income-total',
		fuelExpenseTotalEl: 'finance-fuel-expense-total',
		facilitiesTotalEl: 'finance-facilities-total',
		sponsorshipTotalEl: 'finance-sponsorship-total',
	},
	commercial: {
		sponsorNameEl: 'finance-sponsor-name',
		sponsorReplaceBtn: 'finance-sponsor-replace-btn',
		sponsorAnnualEl: 'finance-sponsor-annual',
		sponsorInstallmentEl: 'finance-sponsor-installment',
		sponsorPaidEl: 'finance-sponsor-paid',
		sponsorRemainingEl: 'finance-sponsor-remaining',
		sponsorLogoWrap: 'finance-sponsor-logo-wrap',
		otherSponsorshipNameEl: 'finance-other-sponsorship-name',
		otherSponsorshipAnnualEl: 'finance-other-sponsorship-annual',
		otherSponsorshipInstallmentEl: 'finance-other-sponsorship-installment',
		otherSponsorshipPaidEl: 'finance-other-sponsorship-paid',
		otherSponsorshipRemainingEl: 'finance-other-sponsorship-remaining',
		otherSponsorshipLogoWrap: 'finance-other-sponsorship-logo-wrap',
	},
	suppliers: {
		engineSupplierReplaceBtn: 'finance-engine-supplier-replace-btn',
		tyreSupplierReplaceBtn: 'finance-tyre-supplier-replace-btn',
		engineSupplierNameEl: 'finance-engine-supplier-name',
		engineSupplierDealEl: 'finance-engine-supplier-deal',
		engineSupplierAnnualEl: 'finance-engine-supplier-annual',
		engineSupplierInstallmentEl: 'finance-engine-supplier-installment',
		engineSupplierPaidEl: 'finance-engine-supplier-paid',
		engineSupplierRemainingEl: 'finance-engine-supplier-remaining',
		engineSupplierLogoWrap: 'finance-engine-supplier-logo-wrap',
		tyreSupplierNameEl: 'finance-tyre-supplier-name',
		tyreSupplierDealEl: 'finance-tyre-supplier-deal',
		tyreSupplierAnnualEl: 'finance-tyre-supplier-annual',
		tyreSupplierInstallmentEl: 'finance-tyre-supplier-installment',
		tyreSupplierPaidEl: 'finance-tyre-supplier-paid',
		tyreSupplierRemainingEl: 'finance-tyre-supplier-remaining',
		tyreSupplierLogoWrap: 'finance-tyre-supplier-logo-wrap',
		fuelSupplierNameEl: 'finance-fuel-supplier-name',
		fuelSupplierDealEl: 'finance-fuel-supplier-deal',
		fuelSupplierAnnualEl: 'finance-fuel-supplier-annual',
		fuelSupplierInstallmentEl: 'finance-fuel-supplier-installment',
		fuelSupplierPaidEl: 'finance-fuel-supplier-paid',
		fuelSupplierRemainingEl: 'finance-fuel-supplier-remaining',
		fuelSupplierLogoWrap: 'finance-fuel-supplier-logo-wrap',
	},
	ledger: {
		trackPlBody: 'finance-track-pl-body',
		tbody: 'finance-transactions-body',
	},
	modals: {
		titleSponsorNegotiationModal: 'finance-title-sponsor-negotiation-modal',
		titleSponsorNegotiationCloseBtn: 'finance-title-sponsor-negotiation-close-btn',
		titleSponsorNegotiationSponsorsEl: 'finance-title-sponsor-negotiation-sponsors',
		titleSponsorNegotiationDetailEl: 'finance-title-sponsor-negotiation-detail',
		engineNegotiationModal: 'finance-engine-negotiation-modal',
		engineNegotiationCloseBtn: 'finance-engine-negotiation-close-btn',
		engineNegotiationSuppliersEl: 'finance-engine-negotiation-suppliers',
		engineNegotiationDetailEl: 'finance-engine-negotiation-detail',
	},
};

export default class FinanceView {
	constructor() {
		this.tabBtns = document.querySelectorAll('.finance-tab-btn');
		this.panels = {
			overview: document.getElementById('finance-content-overview'),
			commercial: document.getElementById('finance-content-commercial'),
			suppliers: document.getElementById('finance-content-suppliers'),
			ledger: document.getElementById('finance-content-ledger'),
		};
		for (const group of Object.values(ELEMENT_GROUPS)) {
			Object.assign(this, this.lookupElements(group));
		}

		this.engineNegotiationData = null;
		this.titleSponsorNegotiationData = null;
		this.onReplaceTitleSponsor = null;
		this.onReplaceEngineSupplier = null;
		this.onReplaceTyreSupplier = null;
		this.onStartEngineNegotiation = null;
		this.onUpdateEngineNegotiationStaff = null;
		this.onSignEngineNegotiatedDeal = null;
		this.onBookEngineNegotiationHospitality = null;
		this.onStartTitleSponsorNegotiation = null;
		this.onUpdateTitleSponsorNegotiationStaff = null;
		this.onSignTitleSponsorNegotiatedDeal = null;
		this.onBookTitleSponsorHospitality = null;

		this.bindTabs();
		this.bindSponsorActions();
		this.bindTitleSponsorNegotiationModal();
		this.bindEngineNegotiationModal();
	}

	lookupElements(group) {
		return Object.fromEntries(
			Object.entries(group).map(([key, id]) => [key, document.getElementById(id)]),
		);
	}

	setReplaceTitleSponsorHandler(handler) { this.onReplaceTitleSponsor = handler; }
	setStartTitleSponsorNegotiationHandler(handler) { this.onStartTitleSponsorNegotiation = handler; }
	setUpdateTitleSponsorNegotiationStaffHandler(handler) { this.onUpdateTitleSponsorNegotiationStaff = handler; }
	setSignTitleSponsorNegotiatedDealHandler(handler) { this.onSignTitleSponsorNegotiatedDeal = handler; }
	setBookTitleSponsorHospitalityHandler(handler) { this.onBookTitleSponsorHospitality = handler; }
	setReplaceTyreSupplierHandler(handler) { this.onReplaceTyreSupplier = handler; }
	setReplaceEngineSupplierHandler(handler) { this.onReplaceEngineSupplier = handler; }
	setStartEngineNegotiationHandler(handler) { this.onStartEngineNegotiation = handler; }
	setUpdateEngineNegotiationStaffHandler(handler) { this.onUpdateEngineNegotiationStaff = handler; }
	setSignEngineNegotiatedDealHandler(handler) { this.onSignEngineNegotiatedDeal = handler; }
	setBookEngineNegotiationHospitalityHandler(handler) { this.onBookEngineNegotiationHospitality = handler; }

	adjustStaffInput(inputId, delta) {
		const input = document.getElementById(inputId);
		if (!input) return null;
		const min = Number(input.min || 0);
		const max = Number(input.max || 0);
		const current = Number(input.value || 0);
		const nextValue = Math.max(min, Math.min(max, current + delta));
		input.value = String(nextValue);
		return nextValue;
	}

	applyStaffFromInput(inputId, handler) {
		const input = document.getElementById(inputId);
		if (!input || !handler) return;
		const min = Number(input.min || 0);
		const max = Number(input.max || 0);
		const nextValue = Math.max(min, Math.min(max, Number(input.value || 0)));
		input.value = String(nextValue);
		handler(nextValue);
	}

	formatMoney(value, options = {}) {
		return formatMoney(value, options);
	}

	applyMoneyState(element, value, { signed = false } = {}) {
		if (!element) return;
		element.textContent = this.formatMoney(value, { signed });
		const amount = Number(value || 0);
		element.className = amount < 0
			? 'finance-balance-amount finance-negative'
			: 'finance-balance-amount';
	}

	setText(element, value) {
		if (element) element.textContent = value;
	}

	setSupplierLogo(targetWrap, supplierName) {
		if (!targetWrap) return;
		if (!supplierName) {
			targetWrap.innerHTML = '';
			return;
		}
		const slug = supplierName.toLowerCase().replace(/\s+/g, '-');
		const fileNameBySlug = { hartek: 'harteck' };
		const preferred = fileNameBySlug[slug] || slug;
		const fallback = `${slug}.png`;
		targetWrap.innerHTML = `
			<img class="supplier-logo" src="assets/supplier_logos/${preferred}.png" alt="${supplierName} logo"
				onerror="if(!this.dataset.f1){this.dataset.f1='1';this.src='assets/supplier_logos/${fallback}';}else{this.style.display='none';}">
		`;
	}

	setSponsorLogo(targetWrap, sponsorName) {
		if (!targetWrap) return;
		if (!sponsorName) {
			targetWrap.innerHTML = '';
			return;
		}
		const encodedOriginal = encodeURIComponent(sponsorName);
		const encodedLower = encodeURIComponent(sponsorName.toLowerCase());
		const encodedUpper = encodeURIComponent(sponsorName.toUpperCase());
		targetWrap.innerHTML = `
			<img class="sponsor-logo" src="assets/sponsor_logos/${encodedOriginal}.png" alt="${sponsorName} logo"
				onerror="if(!this.dataset.f1){this.dataset.f1='1';this.src='assets/sponsor_logos/${encodedLower}.png';}else if(!this.dataset.f2){this.dataset.f2='1';this.src='assets/sponsor_logos/${encodedUpper}.png';}else{this.style.display='none';}">
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
				this.onReplaceTitleSponsor(this.sponsorReplaceBtn.getAttribute('data-sponsor-name') || null);
			});
		}
		if (this.engineSupplierReplaceBtn) {
			this.engineSupplierReplaceBtn.addEventListener('click', () => {
				if (!this.onReplaceEngineSupplier) return;
				this.onReplaceEngineSupplier(this.engineSupplierReplaceBtn.getAttribute('data-supplier-name') || null);
			});
		}
		if (this.tyreSupplierReplaceBtn) {
			this.tyreSupplierReplaceBtn.addEventListener('click', () => {
				if (!this.onReplaceTyreSupplier) return;
				const supplierName = this.tyreSupplierReplaceBtn.getAttribute('data-supplier-name');
				if (supplierName) this.onReplaceTyreSupplier(supplierName);
			});
		}
	}

	bindTitleSponsorNegotiationModal() {
		if (this.titleSponsorNegotiationCloseBtn) {
			this.titleSponsorNegotiationCloseBtn.addEventListener('click', () => this.hideTitleSponsorNegotiationModal());
		}
		if (this.titleSponsorNegotiationModal) {
			this.titleSponsorNegotiationModal.addEventListener('click', (event) => {
				if (event.target === this.titleSponsorNegotiationModal) this.hideTitleSponsorNegotiationModal();
			});
		}
		if (this.titleSponsorNegotiationSponsorsEl) {
			this.titleSponsorNegotiationSponsorsEl.addEventListener('click', (event) => {
				const button = event.target.closest('[data-title-sponsor-id]');
				if (button && this.onStartTitleSponsorNegotiation) {
					this.onStartTitleSponsorNegotiation(Number(button.getAttribute('data-title-sponsor-id')));
				}
			});
		}
		if (this.titleSponsorNegotiationDetailEl) {
			this.titleSponsorNegotiationDetailEl.addEventListener('click', (event) => {
				const stepButton = event.target.closest('[data-staff-step]');
				if (stepButton) {
					const inputId = stepButton.getAttribute('data-staff-input-id');
					this.adjustStaffInput(
						inputId,
						Number(stepButton.getAttribute('data-staff-step') || 0),
					);
					this.applyStaffFromInput(inputId, this.onUpdateTitleSponsorNegotiationStaff);
					return;
				}
				if (event.target.closest('#finance-title-sponsor-negotiation-sign-btn') && this.onSignTitleSponsorNegotiatedDeal) {
					this.onSignTitleSponsorNegotiatedDeal();
					return;
				}
				if (event.target.closest('#finance-title-sponsor-hospitality-btn') && this.onBookTitleSponsorHospitality) {
					this.onBookTitleSponsorHospitality();
				}
			});
			this.titleSponsorNegotiationDetailEl.addEventListener('change', (event) => {
				if (event.target?.id === 'finance-title-sponsor-negotiation-staff') {
					this.applyStaffFromInput(event.target.id, this.onUpdateTitleSponsorNegotiationStaff);
				}
			});
		}
	}

	bindEngineNegotiationModal() {
		if (this.engineNegotiationCloseBtn) {
			this.engineNegotiationCloseBtn.addEventListener('click', () => this.hideEngineNegotiationModal());
		}
		if (this.engineNegotiationModal) {
			this.engineNegotiationModal.addEventListener('click', (event) => {
				if (event.target === this.engineNegotiationModal) this.hideEngineNegotiationModal();
			});
		}
		if (this.engineNegotiationSuppliersEl) {
			this.engineNegotiationSuppliersEl.addEventListener('click', (event) => {
				const button = event.target.closest('[data-engine-supplier-id]');
				if (button && this.onStartEngineNegotiation) {
					this.onStartEngineNegotiation(Number(button.getAttribute('data-engine-supplier-id')));
				}
			});
		}
		if (this.engineNegotiationDetailEl) {
			this.engineNegotiationDetailEl.addEventListener('click', (event) => {
				const stepButton = event.target.closest('[data-staff-step]');
				if (stepButton) {
					const inputId = stepButton.getAttribute('data-staff-input-id');
					this.adjustStaffInput(
						inputId,
						Number(stepButton.getAttribute('data-staff-step') || 0),
					);
					this.applyStaffFromInput(inputId, this.onUpdateEngineNegotiationStaff);
					return;
				}
				const signButton = event.target.closest('[data-engine-tier]');
				if (signButton && this.onSignEngineNegotiatedDeal) {
					this.onSignEngineNegotiatedDeal(signButton.getAttribute('data-engine-tier'));
					return;
				}
				if (event.target.closest('#finance-engine-hospitality-btn') && this.onBookEngineNegotiationHospitality) {
					this.onBookEngineNegotiationHospitality();
				}
			});
			this.engineNegotiationDetailEl.addEventListener('change', (event) => {
				if (event.target?.id === 'finance-engine-negotiation-staff') {
					this.applyStaffFromInput(event.target.id, this.onUpdateEngineNegotiationStaff);
				}
			});
		}
	}

	renderOverview(overview = {}, summary = {}, prizeMeta = {}) {
		this.applyMoneyState(this.balanceEl, prizeMeta.balance || 0);
		this.applyMoneyState(this.netPlEl, summary.net_profit_loss || 0);
		this.applyMoneyState(this.projectedBalanceEl, overview.projected_end_balance || 0);
		this.applyMoneyState(this.nextRaceNetEl, overview.next_race_net || 0);

		this.setText(this.prizeRemainingEl, this.formatMoney(prizeMeta.remaining || 0));
		this.setText(this.prizeProgressEl, `Race installments: ${prizeMeta.racesPaid || 0} / ${prizeMeta.totalRaces || 0}`);
		this.setText(this.prizeOutlookEl, overview.prize_outlook || '-');
		this.setText(this.facilitiesStatusEl, overview.facilities_status || '-');
		this.setText(this.incomeTotalEl, this.formatMoney(summary.income_total || 0));
		this.setText(this.netIncomeTotalEl, this.formatMoney(summary.income_total || 0));
		this.setText(this.netExpenseTotalEl, this.formatMoney(summary.expense_total || 0));
		this.setText(this.netPlBreakdownEl, this.formatMoney(summary.net_profit_loss || 0, { signed: true }));
		this.setText(this.expenseTotalEl, this.formatMoney(summary.expense_total || 0));
		this.setText(this.prizeMoneyTotalEl, this.formatMoney(summary.prize_money_total || 0));
		this.setText(this.payDriverTotalEl, this.formatMoney(summary.pay_driver_income_total || 0));
		this.setText(this.engineIncomeTotalEl, this.formatMoney(summary.engine_supplier_income_total || 0));
		this.setText(this.transportTotalEl, this.formatMoney(summary.transport_total || 0));
		this.setText(this.crashDamageTotalEl, this.formatMoney(summary.crash_damage_total || 0));
		this.setText(this.sparesTotalEl, this.formatMoney(summary.spares_total || 0));
		this.setText(this.testingTotalEl, this.formatMoney(summary.testing_total || 0));
		this.setText(this.driverWagesTotalEl, this.formatMoney(summary.driver_wage_expense_total || 0));
		this.setText(this.managementSalaryTotalEl, this.formatMoney(summary.management_salary_total || 0));
		this.setText(this.designStaffTotalEl, this.formatMoney(summary.design_staff_total || 0));
		this.setText(this.engineeringStaffTotalEl, this.formatMoney(summary.engineering_staff_total || 0));
		this.setText(this.mechanicsStaffTotalEl, this.formatMoney(summary.mechanics_staff_total || 0));
		this.setText(this.commercialStaffTotalEl, this.formatMoney(summary.commercial_staff_total || 0));
		this.setText(this.hospitalityTotalEl, this.formatMoney(summary.hospitality_total || 0));
		this.setText(this.factoryOverheadTotalEl, this.formatMoney(summary.factory_overhead_total || 0));
		this.setText(this.engineSupplierTotalEl, this.formatMoney(summary.engine_supplier_expense_total || 0));
		this.setText(this.tyreSupplierTotalEl, this.formatMoney(summary.tyre_supplier_total || 0));
		this.setText(this.fuelSupplierTotalEl, this.formatMoney(summary.fuel_supplier_total || 0, { signed: true }));
		this.setText(this.fuelIncomeTotalEl, this.formatMoney(summary.fuel_income_total || 0));
		this.setText(this.fuelExpenseTotalEl, this.formatMoney(summary.fuel_expense_total || 0));
		this.setText(this.facilitiesTotalEl, this.formatMoney(summary.facilities_total || 0));
		this.setText(this.sponsorshipTotalEl, this.formatMoney(summary.sponsorship_total || 0));

		if (this.contractAlertsEl) {
			const alerts = Array.isArray(overview.contract_alerts) ? overview.contract_alerts : [];
			this.contractAlertsEl.innerHTML = alerts.length
				? alerts.map((alert) => `<li class="finance-alert-item">${alert}</li>`).join('')
				: '<li class="finance-alert-item">No immediate contract risks.</li>';
		}
	}

	renderCommercial(data) {
		const sponsor = data.sponsor || {};
		const titleSponsorNegotiation = data.title_sponsor_negotiation || this.titleSponsorNegotiationData;
		const sponsorName = sponsor.name || 'Unassigned';
		const sponsorContractLength = sponsor.contract_length || 0;
		const sponsorPendingReplacement = Boolean(sponsor.pending_replacement);

		this.setText(this.sponsorNameEl, sponsorName);
		if (this.sponsorReplaceBtn) {
			const canNegotiate = Boolean(sponsor.name) && sponsorContractLength < 2 && !sponsorPendingReplacement && !titleSponsorNegotiation?.blocked_reason;
			this.sponsorReplaceBtn.disabled = !canNegotiate;
			if (canNegotiate) this.sponsorReplaceBtn.setAttribute('data-sponsor-name', sponsor.name);
			else this.sponsorReplaceBtn.removeAttribute('data-sponsor-name');
		}
		this.setText(this.sponsorAnnualEl, this.formatMoney(sponsor.annual_value || 0));
		this.setText(this.sponsorInstallmentEl, this.formatMoney(sponsor.installment || 0));
		this.setText(this.sponsorPaidEl, this.formatMoney(sponsor.paid_so_far || 0));
		this.setText(this.sponsorRemainingEl, this.formatMoney(sponsor.remaining || 0));
		this.setSponsorLogo(this.sponsorLogoWrap, sponsor.name);

		const otherSponsorship = data.other_sponsorship || {};
		this.setText(this.otherSponsorshipNameEl, 'Minor Sponsors');
		this.setText(this.otherSponsorshipAnnualEl, this.formatMoney(otherSponsorship.annual_value || 0));
		this.setText(this.otherSponsorshipInstallmentEl, this.formatMoney(otherSponsorship.installment || 0));
		this.setText(this.otherSponsorshipPaidEl, this.formatMoney(otherSponsorship.paid_so_far || 0));
		this.setText(this.otherSponsorshipRemainingEl, this.formatMoney(otherSponsorship.remaining || 0));
		if (this.otherSponsorshipLogoWrap) this.otherSponsorshipLogoWrap.innerHTML = '';
	}

	renderSuppliers(data) {
		const engineSupplier = data.engine_supplier || {};
		const engineNegotiation = data.engine_negotiation || this.engineNegotiationData;
		const engineSupplierBuildsOwnEngine = Boolean(engineSupplier.builds_own_engine);
		const engineContractLength = engineSupplier.contract_length || 0;
		const enginePendingReplacement = Boolean(engineSupplier.pending_replacement);
		const engineAnnualSign = (engineSupplier.annual_value || 0) < 0 ? '+' : '-';
		const engineInstallmentSign = engineSupplier.direction === 'income' ? '+' : '-';

		this.setText(this.engineSupplierNameEl, engineSupplier.name || 'Unassigned');
		if (this.engineSupplierReplaceBtn) {
			const canNegotiate = Boolean(engineSupplier.name) && !engineSupplierBuildsOwnEngine && engineContractLength < 2 && !enginePendingReplacement && !engineNegotiation?.blocked_reason;
			this.engineSupplierReplaceBtn.disabled = !canNegotiate;
			if (canNegotiate) this.engineSupplierReplaceBtn.setAttribute('data-supplier-name', engineSupplier.name);
			else this.engineSupplierReplaceBtn.removeAttribute('data-supplier-name');
		}
		this.setText(this.engineSupplierDealEl, engineSupplier.deal || '-');
		this.setText(this.engineSupplierAnnualEl, `${engineAnnualSign}$${Math.abs(engineSupplier.annual_value || 0).toLocaleString()}`);
		this.setText(this.engineSupplierInstallmentEl, `${engineInstallmentSign}$${Math.abs(engineSupplier.installment || 0).toLocaleString()}`);
		this.setText(this.engineSupplierPaidEl, this.formatMoney(engineSupplier.paid_so_far || 0));
		this.setText(this.engineSupplierRemainingEl, this.formatMoney(engineSupplier.remaining || 0));
		this.setSupplierLogo(this.engineSupplierLogoWrap, engineSupplier.name);

		const tyreSupplier = data.tyre_supplier || {};
		const tyreContractLength = tyreSupplier.contract_length || 0;
		const tyrePendingReplacement = Boolean(tyreSupplier.pending_replacement);

		this.setText(this.tyreSupplierNameEl, tyreSupplier.name || 'Unassigned');
		if (this.tyreSupplierReplaceBtn) {
			const canReplace = Boolean(tyreSupplier.name) && tyreContractLength < 2 && !tyrePendingReplacement;
			this.tyreSupplierReplaceBtn.disabled = !canReplace;
			if (canReplace) this.tyreSupplierReplaceBtn.setAttribute('data-supplier-name', tyreSupplier.name);
			else this.tyreSupplierReplaceBtn.removeAttribute('data-supplier-name');
		}
		this.setText(this.tyreSupplierDealEl, tyreSupplier.deal || '-');
		this.setText(this.tyreSupplierAnnualEl, this.formatMoney(tyreSupplier.annual_value || 0));
		this.setText(this.tyreSupplierInstallmentEl, this.formatMoney(tyreSupplier.installment || 0));
		this.setText(this.tyreSupplierPaidEl, this.formatMoney(tyreSupplier.paid_so_far || 0));
		this.setText(this.tyreSupplierRemainingEl, this.formatMoney(tyreSupplier.remaining || 0));
		this.setSupplierLogo(this.tyreSupplierLogoWrap, tyreSupplier.name);

		const fuelSupplier = data.fuel_supplier || {};
		const annualSign = (fuelSupplier.annual_value || 0) < 0 ? '+' : '-';
		const installmentSign = fuelSupplier.direction === 'income' ? '+' : '-';
		this.setText(this.fuelSupplierNameEl, fuelSupplier.name || 'Unassigned');
		this.setText(this.fuelSupplierDealEl, fuelSupplier.deal || '-');
		this.setText(this.fuelSupplierAnnualEl, `${annualSign}$${Math.abs(fuelSupplier.annual_value || 0).toLocaleString()}`);
		this.setText(this.fuelSupplierInstallmentEl, `${installmentSign}$${Math.abs(fuelSupplier.installment || 0).toLocaleString()}`);
		this.setText(this.fuelSupplierPaidEl, this.formatMoney(fuelSupplier.paid_so_far || 0));
		this.setText(this.fuelSupplierRemainingEl, this.formatMoney(fuelSupplier.remaining || 0));
		this.setSupplierLogo(this.fuelSupplierLogoWrap, fuelSupplier.name);
	}

	renderLedger(data) {
		if (this.trackPlBody) this.trackPlBody.innerHTML = renderTrackProfitLossHtml(data.track_profit_loss || []);
		if (this.tbody) this.tbody.innerHTML = renderTransactionsHtml(data.transactions || []);
	}

	render(data) {
		this.engineNegotiationData = data.engine_negotiation || null;
		this.titleSponsorNegotiationData = data.title_sponsor_negotiation || null;
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

	hideTitleSponsorNegotiationModal() {
		if (this.titleSponsorNegotiationModal) this.titleSponsorNegotiationModal.style.display = 'none';
	}

	showTitleSponsorNegotiationModal(data) {
		this.titleSponsorNegotiationData = data;
		if (!this.titleSponsorNegotiationModal) return;
		this.renderTitleSponsorNegotiationModal(data);
		this.titleSponsorNegotiationModal.style.display = 'flex';
	}

	renderTitleSponsorNegotiationModal(data = {}) {
		if (this.titleSponsorNegotiationSponsorsEl) {
			this.titleSponsorNegotiationSponsorsEl.innerHTML = renderTitleSponsorNegotiationSupplierList(Array.isArray(data.sponsors) ? data.sponsors : []);
		}
		if (this.titleSponsorNegotiationDetailEl) {
			this.titleSponsorNegotiationDetailEl.innerHTML = renderTitleSponsorNegotiationDetail(data);
		}
	}

	hideEngineNegotiationModal() {
		if (this.engineNegotiationModal) this.engineNegotiationModal.style.display = 'none';
	}

	showEngineNegotiationModal(data) {
		this.engineNegotiationData = data;
		if (!this.engineNegotiationModal) return;
		this.renderEngineNegotiationModal(data);
		this.engineNegotiationModal.style.display = 'flex';
	}

	renderEngineNegotiationModal(data = {}) {
		if (this.engineNegotiationSuppliersEl) {
			this.engineNegotiationSuppliersEl.innerHTML = renderEngineNegotiationSupplierList(Array.isArray(data.suppliers) ? data.suppliers : []);
		}
		if (this.engineNegotiationDetailEl) {
			this.engineNegotiationDetailEl.innerHTML = renderEngineNegotiationDetail(data);
		}
	}
}
