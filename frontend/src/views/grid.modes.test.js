import { describe, it, expect, beforeEach, vi } from 'vitest';
import GridView from './grid.js';

describe('GridView modes and branch behavior', () => {
	let view;

	beforeEach(() => {
		document.body.innerHTML = `
			<div id="grid-view">
				<select id="grid-mode-toggle">
					<option value="staff">Staff</option>
					<option value="sponsors">Sponsors</option>
					<option value="suppliers">Suppliers</option>
				</select>
				<button class="tab-btn active" data-year="1998">1998</button>
				<button class="tab-btn" data-year="1999">1999</button>
				<div id="grid-content-1998">
					<table>
						<thead id="grid-head-1998"></thead>
						<tbody id="grid-table-body"></tbody>
					</table>
				</div>
				<div id="grid-content-1999" style="display:none;">
					<table>
						<thead id="grid-head-1999"></thead>
						<tbody id="grid-table-body-1999"></tbody>
					</table>
				</div>
			</div>
		`;
		view = new GridView();
	});

	it('updates tab years via setSeasonBase and keeps first tab active', () => {
		view.setSeasonBase(2001);
		const tabs = document.querySelectorAll('.tab-btn[data-year]');
		expect(tabs[0].textContent).toBe('2001');
		expect(tabs[1].textContent).toBe('2002');
		expect(tabs[0].classList.contains('active')).toBe(true);
	});

	it('renders sponsors mode and formatted sponsorship column', () => {
		view.render(
			[
				{
					Team: 'Warrick',
					TitleSponsor: 'Windale',
					TitleSponsorContractLength: 2,
					OtherSponsorshipYearly: 9_500_000,
				},
			],
			1998,
		);
		const toggle = document.getElementById('grid-mode-toggle');
		toggle.value = 'sponsors';
		toggle.dispatchEvent(new Event('change'));

		const head = document.getElementById('grid-head-1998').textContent;
		const row = document.querySelector('#grid-table-body tr');
		expect(head).toContain('Title Sponsor');
		expect(head).toContain('Contract');
		expect(row.innerHTML).toContain('Windale');
		expect(row.innerHTML).toContain('2 year(s)');
		expect(row.innerHTML).toContain('$9,500,000');
	});

	it('renders suppliers mode with capitalized deals and blank vacant supplier', () => {
		view.render(
			[
				{
					Team: 'Swords',
					EngineSupplier: 'Hartek',
					EngineSupplierDeal: 'works',
					TyreSupplier: 'VACANT',
					TyreSupplierDeal: '-',
				},
			],
			1998,
		);
		const toggle = document.getElementById('grid-mode-toggle');
		toggle.value = 'suppliers';
		toggle.dispatchEvent(new Event('change'));

		const row = document.querySelector('#grid-table-body tr');
		expect(row.innerHTML).toContain('Works');
		expect(row.innerHTML).toContain('harteck.png');
		const cells = row.querySelectorAll('td');
		expect(cells[3].textContent.trim()).toBe('');
	});

	it('renders staff mode and triggers driver callback', () => {
		const onDriver = vi.fn();
		view.setDriverSelectHandler(onDriver);
		view.render(
			[
				{
					Team: 'Warrick',
					Driver1: 'John Newhouse',
					Driver1Country: 'Canada',
					Driver2: 'VACANT',
					TechnicalDirector: 'Peter Heed',
					TechnicalDirectorCountry: 'United Kingdom',
					CommercialManager: 'Jace Whitman',
				},
			],
			1998,
		);

		const link = document.querySelector('.driver-link[data-driver-name="John Newhouse"]');
		expect(link).toBeTruthy();
		link.click();
		expect(onDriver).toHaveBeenCalledWith('John Newhouse');
	});
});
