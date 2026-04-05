import { describe, it, expect, beforeEach } from 'vitest';
import { renderLayoutPartials } from './partials.js';

describe('layout partials', () => {
	beforeEach(() => {
		document.body.innerHTML = `
			<div id="finance-summary"></div>
			<div id="finance-overview-breakdown"></div>
			<div id="finance-overview-planning"></div>
			<ul id="finance-contract-alerts"></ul>
			<div id="finance-commercial-sections"></div>
			<div id="finance-supplier-sections"></div>
		`;
	});

	it('renders finance cards and supplier sections in expected order', () => {
		renderLayoutPartials();

		const summary = document.getElementById('finance-summary');
		const commercialSections = document.getElementById('finance-commercial-sections');
		const supplierSections = document.getElementById('finance-supplier-sections');
		expect(summary.querySelectorAll('.finance-balance-card').length).toBe(5);
		expect(document.getElementById('finance-projected-balance')).toBeTruthy();
		expect(document.getElementById('finance-next-race-income')).toBeTruthy();

		const commercialCards = [...commercialSections.querySelectorAll('.finance-sponsor-card')];
		expect(commercialCards.map((card) => card.querySelector('.finance-balance-label')?.textContent?.trim())).toEqual([
			'Title Sponsor',
			'Other Sponsorship',
		]);

		const cards = [...supplierSections.querySelectorAll('.finance-sponsor-card')];
		const titles = cards.map((card) => card.querySelector('.finance-balance-label')?.textContent?.trim());
		expect(titles).toEqual([
			'Engine Supplier',
			'Tyre Supplier',
			'Fuel Supplier',
		]);
		expect(document.getElementById('finance-sponsor-replace-btn')).toBeTruthy();
	});

	it('is safe when containers are missing', () => {
		document.body.innerHTML = `<div id="unrelated"></div>`;
		expect(() => renderLayoutPartials()).not.toThrow();
	});
});
