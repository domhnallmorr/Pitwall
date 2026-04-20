import {
	renderEngineNegotiationDetail,
	renderEngineNegotiationSupplierList,
	renderTitleSponsorNegotiationDetail,
	renderTitleSponsorNegotiationSupplierList,
} from './finance_renderers.js';

export default class CommercialView {
	constructor() {
		this.summaryEl = document.getElementById('commercial-summary');
		this.tabBtns = document.querySelectorAll('.commercial-tab-btn');
		this.titleSponsorPanel = document.getElementById('commercial-content-title-sponsor');
		this.enginePanel = document.getElementById('commercial-content-engine');
		this.titleSponsorListEl = document.getElementById('commercial-title-sponsor-list');
		this.titleSponsorDetailEl = document.getElementById('commercial-title-sponsor-detail');
		this.engineListEl = document.getElementById('commercial-engine-list');
		this.engineDetailEl = document.getElementById('commercial-engine-detail');
		this.hospitalityModal = document.getElementById('commercial-hospitality-modal');
		this.hospitalityModalTitle = document.getElementById('commercial-hospitality-modal-title');
		this.hospitalityModalBody = document.getElementById('commercial-hospitality-modal-body');
		this.hospitalityCancelBtn = document.getElementById('commercial-hospitality-cancel-btn');
		this.hospitalityConfirmBtn = document.getElementById('commercial-hospitality-confirm-btn');

		this.activeTab = 'title-sponsor';
		this.titleSponsorData = null;
		this.engineData = null;
		this.summaryData = null;
		this.pendingHospitalityAction = null;

		this.onStartTitleSponsorNegotiation = null;
		this.onUpdateTitleSponsorNegotiationStaff = null;
		this.onSignTitleSponsorNegotiatedDeal = null;
		this.onBookTitleSponsorHospitality = null;
		this.onStartEngineNegotiation = null;
		this.onUpdateEngineNegotiationStaff = null;
		this.onSignEngineNegotiatedDeal = null;
		this.onBookEngineNegotiationHospitality = null;

		this.bindTabs();
		this.bindTitleSponsorPanel();
		this.bindEnginePanel();
		this.bindHospitalityModal();
	}

	setStartTitleSponsorNegotiationHandler(handler) { this.onStartTitleSponsorNegotiation = handler; }
	setUpdateTitleSponsorNegotiationStaffHandler(handler) { this.onUpdateTitleSponsorNegotiationStaff = handler; }
	setSignTitleSponsorNegotiatedDealHandler(handler) { this.onSignTitleSponsorNegotiatedDeal = handler; }
	setBookTitleSponsorHospitalityHandler(handler) { this.onBookTitleSponsorHospitality = handler; }
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

	bindTabs() {
		this.tabBtns.forEach((btn) => {
			btn.addEventListener('click', () => this.showTab(btn.getAttribute('data-type')));
		});
	}

	bindTitleSponsorPanel() {
		if (this.titleSponsorListEl) {
			this.titleSponsorListEl.addEventListener('click', (event) => {
				const button = event.target.closest('[data-title-sponsor-id]');
				if (button && this.onStartTitleSponsorNegotiation) {
					this.onStartTitleSponsorNegotiation(Number(button.getAttribute('data-title-sponsor-id')));
				}
			});
		}
		if (this.titleSponsorDetailEl) {
			this.titleSponsorDetailEl.addEventListener('click', (event) => {
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
				if (event.target.closest('#commercial-title-sponsor-negotiation-sign-btn') && this.onSignTitleSponsorNegotiatedDeal) {
					this.onSignTitleSponsorNegotiatedDeal();
					return;
				}
				if (event.target.closest('#commercial-title-sponsor-hospitality-btn') && this.onBookTitleSponsorHospitality) {
					this.openHospitalityConfirm('title-sponsor');
				}
			});
			this.titleSponsorDetailEl.addEventListener('change', (event) => {
				if (event.target?.id === 'commercial-title-sponsor-negotiation-staff') {
					this.applyStaffFromInput(event.target.id, this.onUpdateTitleSponsorNegotiationStaff);
				}
			});
		}
	}

	bindEnginePanel() {
		if (this.engineListEl) {
			this.engineListEl.addEventListener('click', (event) => {
				const button = event.target.closest('[data-engine-supplier-id]');
				if (button && this.onStartEngineNegotiation) {
					this.onStartEngineNegotiation(Number(button.getAttribute('data-engine-supplier-id')));
				}
			});
		}
		if (this.engineDetailEl) {
			this.engineDetailEl.addEventListener('click', (event) => {
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
				if (event.target.closest('#commercial-engine-hospitality-btn') && this.onBookEngineNegotiationHospitality) {
					this.openHospitalityConfirm('engine');
				}
			});
			this.engineDetailEl.addEventListener('change', (event) => {
				if (event.target?.id === 'commercial-engine-negotiation-staff') {
					this.applyStaffFromInput(event.target.id, this.onUpdateEngineNegotiationStaff);
				}
			});
		}
	}

	bindHospitalityModal() {
		if (this.hospitalityCancelBtn) {
			this.hospitalityCancelBtn.addEventListener('click', () => this.closeHospitalityConfirm());
		}
		if (this.hospitalityConfirmBtn) {
			this.hospitalityConfirmBtn.addEventListener('click', () => {
				if (this.pendingHospitalityAction === 'title-sponsor' && this.onBookTitleSponsorHospitality) {
					this.onBookTitleSponsorHospitality();
				} else if (this.pendingHospitalityAction === 'engine' && this.onBookEngineNegotiationHospitality) {
					this.onBookEngineNegotiationHospitality();
				}
				this.closeHospitalityConfirm();
			});
		}
		if (this.hospitalityModal) {
			this.hospitalityModal.addEventListener('click', (event) => {
				if (event.target === this.hospitalityModal) this.closeHospitalityConfirm();
			});
		}
	}

	openHospitalityConfirm(targetType) {
		const data = targetType === 'title-sponsor' ? this.titleSponsorData : this.engineData;
		const hospitality = data?.hospitality || {};
		const targetName = targetType === 'title-sponsor'
			? data?.active_negotiation?.sponsor_name
			: data?.active_negotiation?.supplier_name;
		const eventLabel = hospitality.event_name
			? `${hospitality.event_name}${hospitality.event_week ? ` (Week ${hospitality.event_week})` : ''}`
			: 'the next race';
		if (!this.hospitalityModal) return;
		this.pendingHospitalityAction = targetType;
		if (this.hospitalityModalTitle) {
			this.hospitalityModalTitle.textContent = 'Confirm Hospitality Invite';
		}
		if (this.hospitalityModalBody) {
			this.hospitalityModalBody.textContent = `Invite ${targetName || 'this negotiation partner'} to ${eventLabel} for $${Number(hospitality.cost || 0).toLocaleString()}?`;
		}
		this.hospitalityModal.style.display = 'flex';
	}

	closeHospitalityConfirm() {
		this.pendingHospitalityAction = null;
		if (this.hospitalityModal) this.hospitalityModal.style.display = 'none';
	}

	showTab(type = 'title-sponsor') {
		this.activeTab = type;
		this.tabBtns.forEach((btn) => btn.classList.toggle('active', btn.getAttribute('data-type') === type));
		if (this.titleSponsorPanel) this.titleSponsorPanel.style.display = type === 'title-sponsor' ? 'block' : 'none';
		if (this.enginePanel) this.enginePanel.style.display = type === 'engine' ? 'block' : 'none';
		this.renderSummary();
	}

	renderSummary() {
		if (!this.summaryEl) return;
		const finance = this.summaryData || {};
		const titleNegotiation = this.titleSponsorData || {};
		const engineNegotiation = this.engineData || {};
		const manager = titleNegotiation.commercial_manager || engineNegotiation.commercial_manager || {};
		const commercialStaffTotal = Number(titleNegotiation.commercial_staff_total || engineNegotiation.commercial_staff_total || 0);
		const activeTalks = [titleNegotiation.active_negotiation, engineNegotiation.active_negotiation].filter(Boolean).length;
		const activeHospitality = titleNegotiation.hospitality?.booked
			? 'Title Sponsor booked'
			: engineNegotiation.hospitality?.booked
				? 'Engine Supplier booked'
				: 'None booked';

		this.summaryEl.innerHTML = `
			<div class="commercial-summary-card">
				<div class="finance-balance-label">Commercial Manager</div>
				<div class="commercial-summary-value">${manager.name || 'Unassigned'}</div>
				<div class="commercial-summary-subtle">Skill ${manager.skill || 0}</div>
			</div>
			<div class="commercial-summary-card">
				<div class="finance-balance-label">Commercial Staff</div>
				<div class="commercial-summary-value">${commercialStaffTotal}</div>
				<div class="commercial-summary-subtle">Average staff available for talks</div>
			</div>
			<div class="commercial-summary-card">
				<div class="finance-balance-label">Active Talks</div>
				<div class="commercial-summary-value">${activeTalks}</div>
				<div class="commercial-summary-subtle">Title sponsor and engine negotiations</div>
			</div>
			<div class="commercial-summary-card">
				<div class="finance-balance-label">Hospitality</div>
				<div class="commercial-summary-value">${activeHospitality}</div>
				<div class="commercial-summary-subtle">Current sponsor: ${finance.sponsor?.name || 'Unassigned'} | Engine: ${finance.engine_supplier?.name || 'Unassigned'}</div>
			</div>
		`;
	}

	renderTitleSponsorNegotiation(data = {}) {
		this.titleSponsorData = data;
		if (this.titleSponsorListEl) {
			this.titleSponsorListEl.innerHTML = renderTitleSponsorNegotiationSupplierList(Array.isArray(data.sponsors) ? data.sponsors : []);
		}
		if (this.titleSponsorDetailEl) {
			this.titleSponsorDetailEl.innerHTML = renderTitleSponsorNegotiationDetail(data, {
				staffInputId: 'commercial-title-sponsor-negotiation-staff',
				signButtonId: 'commercial-title-sponsor-negotiation-sign-btn',
				hospitalityButtonId: 'commercial-title-sponsor-hospitality-btn',
			});
		}
		this.renderSummary();
	}

	renderEngineNegotiation(data = {}) {
		this.engineData = data;
		if (this.engineListEl) {
			this.engineListEl.innerHTML = renderEngineNegotiationSupplierList(Array.isArray(data.suppliers) ? data.suppliers : []);
		}
		if (this.engineDetailEl) {
			this.engineDetailEl.innerHTML = renderEngineNegotiationDetail(data, {
				staffInputId: 'commercial-engine-negotiation-staff',
				hospitalityButtonId: 'commercial-engine-hospitality-btn',
			});
		}
		this.renderSummary();
	}

	render(financeData = {}) {
		this.summaryData = financeData;
		this.renderTitleSponsorNegotiation(financeData.title_sponsor_negotiation || {});
		this.renderEngineNegotiation(financeData.engine_negotiation || {});
	}
}
