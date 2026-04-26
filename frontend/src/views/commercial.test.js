import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import CommercialView from './commercial.js';

describe('CommercialView', () => {
	let view;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="commercial-view">
				<div id="commercial-summary"></div>
				<button class="commercial-tab-btn active" data-type="title-sponsor"></button>
				<button class="commercial-tab-btn" data-type="engine"></button>
				<div id="commercial-content-title-sponsor">
					<div id="commercial-title-sponsor-list"></div>
					<div id="commercial-title-sponsor-detail"></div>
				</div>
				<div id="commercial-content-engine" style="display:none;">
					<div id="commercial-engine-list"></div>
					<div id="commercial-engine-detail"></div>
				</div>
				<div id="commercial-hospitality-modal" style="display:none;">
					<div id="commercial-hospitality-modal-title"></div>
					<div id="commercial-hospitality-modal-body"></div>
					<button id="commercial-hospitality-cancel-btn"></button>
					<button id="commercial-hospitality-confirm-btn"></button>
				</div>
			</div>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		view = new CommercialView();
	});

	it('renders summary cards and both negotiation panels from finance data', () => {
		view.render({
			sponsor: { name: 'Windale' },
			engine_supplier: { name: 'Mechatron' },
			title_sponsor_negotiation: {
				sponsors: [{ id: 1, name: 'Fastlane', wealth: 74, targetable: true }],
				commercial_manager: { name: 'Helena Schwarz', skill: 84 },
				commercial_staff_total: 49,
				hospitality: { booked: false },
			},
			engine_negotiation: {
				suppliers: [{ id: 2, name: 'Mechatron', country: 'Germany', power: 88, resources: 84, targetable: true }],
				commercial_manager: { name: 'Helena Schwarz', skill: 84 },
				commercial_staff_total: 49,
				hospitality: { booked: true },
			},
		});

		expect(document.getElementById('commercial-summary').textContent).toContain('Helena Schwarz');
		expect(document.getElementById('commercial-summary').textContent).toContain('Windale');
		expect(document.getElementById('commercial-summary').textContent).toContain('Mechatron');
		expect(document.getElementById('commercial-title-sponsor-list').textContent).toContain('Fastlane');
		expect(document.getElementById('commercial-engine-list').textContent).toContain('Power 88');
	});

	it('switches tabs and routes sponsor actions through handlers', () => {
		const onStart = vi.fn();
		const onUpdateStaff = vi.fn();
		const onSign = vi.fn();
		const onHospitality = vi.fn();
		view.setStartTitleSponsorNegotiationHandler(onStart);
		view.setUpdateTitleSponsorNegotiationStaffHandler(onUpdateStaff);
		view.setSignTitleSponsorNegotiatedDealHandler(onSign);
		view.setBookTitleSponsorHospitalityHandler(onHospitality);

		view.renderTitleSponsorNegotiation({
			sponsors: [{ id: 7, name: 'Fastlane', wealth: 74, targetable: true }],
			commercial_manager: { name: 'Helena Schwarz', skill: 84 },
			commercial_staff_total: 49,
			hospitality: { available: true, booked: false, cost: 100000, progress_bonus: 1.0, event_name: 'Albert Park', event_week: 10 },
			active_negotiation: {
				sponsor_name: 'Fastlane',
				progress_boxes: 3,
				total_boxes: 5,
				annual_value: 12000000,
				contract_length: 2,
				assigned_staff: 12,
				ready_to_sign: true,
			},
		});

		document.querySelector('[data-title-sponsor-id="7"]').click();
		expect(onStart).toHaveBeenCalledWith(7);

		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="1"]').click();
		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="1"]').click();
		const input = document.getElementById('commercial-title-sponsor-negotiation-staff');
		document.getElementById('commercial-title-sponsor-negotiation-sign-btn').click();
		document.getElementById('commercial-title-sponsor-hospitality-btn').click();
		expect(document.getElementById('commercial-hospitality-modal').style.display).toBe('flex');
		expect(document.getElementById('commercial-hospitality-modal-body').textContent).toContain('Albert Park (Week 10)');
		document.getElementById('commercial-hospitality-confirm-btn').click();

		expect(input.value).toBe('14');
		expect(onUpdateStaff).toHaveBeenNthCalledWith(1, 13);
		expect(onUpdateStaff).toHaveBeenNthCalledWith(2, 14);
		expect(onSign).toHaveBeenCalled();
		expect(onHospitality).toHaveBeenCalled();

		document.querySelector('.commercial-tab-btn[data-type="engine"]').click();
		expect(document.getElementById('commercial-content-title-sponsor').style.display).toBe('none');
		expect(document.getElementById('commercial-content-engine').style.display).toBe('block');
	});

	it('routes engine actions through handlers and applies typed staff changes', () => {
		const onStart = vi.fn();
		const onUpdateStaff = vi.fn();
		const onSign = vi.fn();
		const onHospitality = vi.fn();
		view.setStartEngineNegotiationHandler(onStart);
		view.setUpdateEngineNegotiationStaffHandler(onUpdateStaff);
		view.setSignEngineNegotiatedDealHandler(onSign);
		view.setBookEngineNegotiationHospitalityHandler(onHospitality);

		view.renderEngineNegotiation({
			suppliers: [{ id: 2, name: 'Mechatron', country: 'Germany', power: 88, resources: 84, targetable: true }],
			commercial_manager: { name: 'Helena Schwarz', skill: 84 },
			commercial_staff_total: 20,
			hospitality: { available: true, booked: false, cost: 100000, progress_bonus: 1.0, event_name: 'Interlagos', event_week: 12 },
			active_negotiation: {
				supplier_name: 'Mechatron',
				assigned_staff: 12,
				progress_boxes: 5,
				total_boxes: 8,
				customer_threshold: 3,
				partner_threshold: 5,
				works_threshold: 8,
				contract_length: 2,
				available_tiers: ['customer', 'partner', 'works'],
				unlocked_tiers: ['customer', 'partner'],
				annual_values: {
					customer: -10000000,
					partner: -12000000,
					works: -15000000,
				},
			},
		});

		document.querySelector('[data-engine-supplier-id="2"]').click();
		expect(onStart).toHaveBeenCalledWith(2);

		const input = document.getElementById('commercial-engine-negotiation-staff');
		input.value = '50';
		input.dispatchEvent(new window.Event('change', { bubbles: true }));
		expect(input.value).toBe('20');
		expect(onUpdateStaff).toHaveBeenCalledWith(20);

		document.querySelector('[data-staff-input-id="commercial-engine-negotiation-staff"][data-staff-step="-1"]').click();
		expect(onUpdateStaff).toHaveBeenLastCalledWith(19);

		document.querySelector('[data-engine-tier="customer"]').click();
		expect(onSign).toHaveBeenCalledWith('customer');

		document.getElementById('commercial-engine-hospitality-btn').click();
		expect(document.getElementById('commercial-hospitality-modal-body').textContent).toContain('Interlagos (Week 12)');
		document.getElementById('commercial-hospitality-confirm-btn').click();
		expect(onHospitality).toHaveBeenCalled();
	});

	it('clamps staff stepper values and supports hospitality cancel/overlay close', () => {
		view.setUpdateTitleSponsorNegotiationStaffHandler(vi.fn());
		view.renderTitleSponsorNegotiation({
			sponsors: [],
			commercial_staff_total: 3,
			hospitality: { available: true, booked: false, cost: 100000, progress_bonus: 1.0 },
			active_negotiation: {
				sponsor_name: 'Fastlane',
				progress_boxes: 1,
				total_boxes: 5,
				annual_value: 5000000,
				contract_length: 1,
				assigned_staff: 0,
				ready_to_sign: false,
			},
		});

		const input = document.getElementById('commercial-title-sponsor-negotiation-staff');
		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="-1"]').click();
		expect(input.value).toBe('0');

		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="1"]').click();
		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="1"]').click();
		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="1"]').click();
		document.querySelector('[data-staff-input-id="commercial-title-sponsor-negotiation-staff"][data-staff-step="1"]').click();
		expect(input.value).toBe('3');

		view.openHospitalityConfirm('title-sponsor');
		expect(document.getElementById('commercial-hospitality-modal').style.display).toBe('flex');
		document.getElementById('commercial-hospitality-cancel-btn').click();
		expect(document.getElementById('commercial-hospitality-modal').style.display).toBe('none');

		view.openHospitalityConfirm('title-sponsor');
		document.getElementById('commercial-hospitality-modal').dispatchEvent(
			new window.MouseEvent('click', { bubbles: true }),
		);
		expect(document.getElementById('commercial-hospitality-modal').style.display).toBe('none');
	});

	it('renders summary fallback values when no talks are active', () => {
		view.render({
			sponsor: {},
			engine_supplier: {},
			title_sponsor_negotiation: {
				sponsors: [],
				hospitality: { booked: false },
			},
			engine_negotiation: {
				suppliers: [],
				hospitality: { booked: false },
			},
		});

		const summary = document.getElementById('commercial-summary').textContent;
		expect(summary).toContain('Unassigned');
		expect(summary).toContain('0');
		expect(summary).toContain('None booked');
	});
});
