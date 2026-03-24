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
				<table>
					<thead><tr></tr></thead>
					<tbody id="driver-market-table-body"></tbody>
				</table>
			</div>
		`);
		global.document = dom.window.document;
		global.window = dom.window;
		marketView = new DriverMarketView();
	});

	it('renders candidates and triggers sign callback', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			outgoing_driver: { id: 1, name: 'Old Driver' },
			candidates: [{ id: 99, name: 'Free Agent', age: 24, country: 'Germany', speed: 80, wage: 0, pay_driver: false }],
		});

		const btn = document.querySelector('.driver-market-sign-btn');
		expect(btn).not.toBeNull();
		btn.click();
		expect(onSign).toHaveBeenCalledWith(1, 99, 'driver');
	});

	it('renders empty candidates state and supports back action', () => {
		const onBack = vi.fn();
		marketView.setBackHandler(onBack);
		marketView.render({ outgoing_driver: { id: 1, name: 'Old Driver' }, candidates: [] });

		expect(document.getElementById('driver-market-title').textContent).toContain('Replace Old Driver');
		expect(document.getElementById('driver-market-table-body').textContent).toContain('No available candidates');

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

		expect(document.getElementById('driver-market-title').textContent).toContain('Replace Old Manager');
		const head = document.querySelector('#driver-market-view thead tr').textContent;
		expect(head).toContain('Salary');

		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith(11, 12, 'commercial_manager');
	});

	it('renders technical director market and signs director candidate', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'technical_director',
			outgoing_manager: { id: 21, name: 'Old TD' },
			candidates: [{ id: 22, name: 'Free TD', age: 44, country: 'France', skill: 68, salary: 480000 }],
		});

		expect(document.getElementById('driver-market-title').textContent).toContain('Replace Old TD');
		const head = document.querySelector('#driver-market-view thead tr').textContent;
		expect(head).toContain('Salary');

		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith(21, 22, 'technical_director');
	});

	it('renders title sponsor market and signs sponsor candidate', () => {
		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'title_sponsor',
			outgoing_sponsor: { name: 'Windale' },
			candidates: [{ id: 32, name: 'Bright Shot', wealth: 85, start_year: 0 }],
		});

		expect(document.getElementById('driver-market-title').textContent).toContain('Replace Windale');
		const head = document.querySelector('#driver-market-view thead tr').textContent;
		expect(head).toContain('Wealth');

		const btn = document.querySelector('.driver-market-sign-btn');
		btn.click();
		expect(onSign).toHaveBeenCalledWith('Windale', 32, 'title_sponsor');
	});

	it('ignores sign clicks when no handlers or missing outgoing entities', () => {
		marketView.render({
			outgoing_driver: null,
			candidates: [{ id: 15, name: 'Candidate', age: 21, country: 'Italy', speed: 70, wage: 1000, pay_driver: false }],
		});
		const btn = document.querySelector('.driver-market-sign-btn');
		expect(() => btn.click()).not.toThrow();

		const onSign = vi.fn();
		marketView.setSignHandler(onSign);
		marketView.render({
			market_type: 'commercial_manager',
			outgoing_manager: null,
			candidates: [{ id: 16, name: 'CM', age: 35, country: 'UK', skill: 60, salary: 1000 }],
		});
		document.querySelector('.driver-market-sign-btn').click();
		expect(onSign).not.toHaveBeenCalled();
	});

	it('returns early when required DOM nodes are missing', () => {
		document.body.innerHTML = `<div id="driver-market-view"></div>`;
		const view = new DriverMarketView();
		expect(() => view.render({ candidates: [] })).not.toThrow();
	});
});
