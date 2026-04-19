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

		const input = document.getElementById('commercial-title-sponsor-negotiation-staff');
		input.value = '18';
		document.getElementById('commercial-title-sponsor-negotiation-apply-staff').click();
		document.getElementById('commercial-title-sponsor-negotiation-sign-btn').click();
		document.getElementById('commercial-title-sponsor-hospitality-btn').click();
		expect(document.getElementById('commercial-hospitality-modal').style.display).toBe('flex');
		expect(document.getElementById('commercial-hospitality-modal-body').textContent).toContain('Albert Park (Week 10)');
		document.getElementById('commercial-hospitality-confirm-btn').click();

		expect(onUpdateStaff).toHaveBeenCalledWith(18);
		expect(onSign).toHaveBeenCalled();
		expect(onHospitality).toHaveBeenCalled();

		document.querySelector('.commercial-tab-btn[data-type="engine"]').click();
		expect(document.getElementById('commercial-content-title-sponsor').style.display).toBe('none');
		expect(document.getElementById('commercial-content-engine').style.display).toBe('block');
	});
});
