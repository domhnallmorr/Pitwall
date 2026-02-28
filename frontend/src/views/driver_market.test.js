import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import DriverMarketView from './driver_market.js';

describe('DriverMarketView', () => {
	let marketView;

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="driver-market-view"></div>
			<h2 id="driver-market-title"></h2>
			<button id="driver-market-back-btn"></button>
			<table><tbody id="driver-market-table-body"></tbody></table>
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
		expect(onSign).toHaveBeenCalledWith(1, 99);
	});
});
