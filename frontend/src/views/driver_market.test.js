import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import DriverMarketView from './driver_market.js';

describe('DriverMarketView', () => {
	let marketView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<h2 id="driver-market-title"></h2>
			<button id="driver-market-back-btn"></button>
			<div id="driver-market-view">
				<div id="driver-market-driver-workspace" style="display:none;">
					<div id="driver-market-driver-list"></div>
					<div id="driver-market-driver-detail"></div>
				</div>
				<div id="driver-market-table-wrap">
					<table>
						<thead><tr></tr></thead>
						<tbody id="driver-market-table-body"></tbody>
					</table>
				</div>
				<div id="driver-market-offer-modal" style="display:none;">
					<h2 id="driver-market-offer-title"></h2>
					<div id="driver-market-offer-driver"></div>
					<div id="driver-market-offer-status"></div>
					<select id="driver-market-offer-contract">
						<option value="1">1 year</option>
						<option value="2">2 years</option>
						<option value="3">3 years</option>
					</select>
					<input id="driver-market-offer-salary" type="number">
					<button id="driver-market-offer-cancel-btn"></button>
					<button id="driver-market-offer-confirm-btn"></button>
				</div>
				<div id="driver-market-result-modal" style="display:none;">
					<div id="driver-market-result-kicker"></div>
					<h2 id="driver-market-result-title"></h2>
					<div id="driver-market-result-message"></div>
					<div id="driver-market-result-meta"></div>
					<button id="driver-market-result-close-btn"></button>
				</div>
			</div>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		marketView = new DriverMarketView();
	});

	it('renders driver shortlist and detail panel', () => {
		marketView.render({
			outgoing_driver: { id: 1, name: 'Old Driver' },
			candidates: [
				{ id: 100, name: 'Expiring Seat', age: 28, country: 'Italy', speed: 72, wage: 500000, pay_driver: false, contract_length: 1, team_name: 'Ferano' },
				{ id: 99, name: 'Free Agent', age: 24, country: 'Germany', speed: 80, wage: 0, pay_driver: false, contract_length: 0 },
			],
		});

		expect(document.getElementById('driver-market-driver-workspace').style.display).toBe('grid');
		expect(document.getElementById('driver-market-table-wrap').style.display).toBe('none');
		const listButtons = document.querySelectorAll('.driver-market-list-item');
		expect(listButtons[0].textContent).toContain('Free Agent');
		expect(listButtons[1].textContent).toContain('Expiring Seat');
		expect(document.getElementById('driver-market-driver-list').textContent).not.toContain('Expiring Contract');
		expect(document.getElementById('driver-market-driver-list').textContent).not.toContain('Germany');
		expect(document.getElementById('driver-market-driver-detail').textContent).toContain('Current Team');
		expect(document.getElementById('driver-market-driver-detail').textContent).toContain('Free Agent');
		expect(document.getElementById('driver-market-driver-detail').innerHTML).toContain('Speed rating 4 out of 5');
		expect(document.getElementById('driver-market-driver-detail').textContent).not.toContain('80');
	});

	it('opens offer modal and submits driver offer callback', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			outgoing_driver: { id: 1, name: 'Old Driver' },
			candidates: [{ id: 99, name: 'Free Agent', age: 24, country: 'Germany', speed: 80, wage: 0, pay_driver: false, contract_length: 0 }],
		});

		document.querySelector('.driver-market-offer-btn').click();
		expect(document.getElementById('driver-market-offer-modal').style.display).toBe('flex');
		document.getElementById('driver-market-offer-contract').value = '3';
		document.getElementById('driver-market-offer-salary').value = '900000';
		document.getElementById('driver-market-offer-confirm-btn').click();

		expect(onSign).toHaveBeenCalledWith(1, 99, 'driver', { salary: 900000, contract_length: 3 });
		expect(document.getElementById('driver-market-offer-modal').style.display).toBe('none');
	});

	it('disables offer path for unavailable contracted drivers', () => {
		marketView.render({
			outgoing_driver: { id: 1, name: 'Old Driver' },
			candidates: [{ id: 101, name: 'Locked Driver', age: 27, country: 'France', speed: 84, wage: 1200000, pay_driver: false, contract_length: 3, team_name: 'McAlister' }],
		});

		expect(document.getElementById('driver-market-driver-detail').textContent).toContain('Under Contract');
		expect(document.querySelector('.driver-market-offer-btn').disabled).toBe(true);
		document.querySelector('.driver-market-offer-btn').click();
		expect(document.getElementById('driver-market-offer-modal').style.display).toBe('none');
	});

	it('renders a styled offer result modal and runs close callback', () => {
		const onClose = vi.fn();
		const shown = marketView.showOfferResult({
			accepted: true,
			message: 'Driver accepted.',
			driver_name: 'Free Agent',
			interest_band: 'Interested',
			salary: 900000,
			contract_length: 2,
		}, onClose);

		expect(shown).toBe(true);
		expect(document.getElementById('driver-market-result-modal').style.display).toBe('flex');
		expect(document.getElementById('driver-market-result-title').textContent).toContain('Deal Agreed');
		expect(document.getElementById('driver-market-result-message').textContent).toContain('Driver accepted.');
		expect(document.getElementById('driver-market-result-meta').textContent).toContain('Free Agent');

		document.getElementById('driver-market-result-close-btn').click();
		expect(document.getElementById('driver-market-result-modal').style.display).toBe('none');
		expect(onClose).toHaveBeenCalledTimes(1);
	});

	it('renders empty candidates state and supports back action', () => {
		const onBack = vi.fn();
		marketView.setBackHandler(onBack);
		marketView.render({ outgoing_driver: { id: 1, name: 'Old Driver' }, candidates: [] });

		expect(document.getElementById('driver-market-title').textContent).toContain('Replace Old Driver');
		expect(document.getElementById('driver-market-driver-list').textContent).toContain('No available candidates');

		document.getElementById('driver-market-back-btn').click();
		expect(onBack).toHaveBeenCalledTimes(1);
	});

	it('renders commercial manager market and signs manager candidate', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'commercial_manager',
			outgoing_manager: { id: 11, name: 'Old Manager' },
			candidates: [{ id: 12, name: 'Free CM', age: 40, country: 'France', skill: 55, salary: 320000 }],
		});

		expect(document.getElementById('driver-market-driver-workspace').style.display).toBe('none');
		expect(document.getElementById('driver-market-table-wrap').style.display).toBe('block');
		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith(11, 12, 'commercial_manager');
	});

	it('renders title sponsor market and signs sponsor candidate', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'title_sponsor',
			outgoing_sponsor: { name: 'Windale' },
			candidates: [{ id: 32, name: 'Bright Shot', wealth: 85, start_year: 0 }],
		});

		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith('Windale', 32, 'title_sponsor');
	});

	it('renders tyre supplier market and signs supplier candidate', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'tyre_supplier',
			outgoing_supplier: { name: 'Greatday' },
			candidates: [{ id: 42, name: 'Spanrock', country: 'Japan', grip: 70, wear: 80 }],
		});

		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith('Greatday', 42, 'tyre_supplier');
	});

	it('renders engine supplier market and signs supplier candidate', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'engine_supplier',
			outgoing_supplier: { name: 'Mechatron' },
			candidates: [{ id: 52, name: 'Frost', country: 'USA', power: 38, resources: 65 }],
		});

		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith('Mechatron', 52, 'engine_supplier');
	});

	it('returns early when required DOM nodes are missing', () => {
		document.body.innerHTML = `<div id="driver-market-view"></div>`;
		const view = new DriverMarketView();
		expect(() => view.render({ candidates: [] })).not.toThrow();
	});
});
