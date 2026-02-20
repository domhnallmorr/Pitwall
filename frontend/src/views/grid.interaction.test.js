import { describe, it, expect, beforeEach, vi } from 'vitest';
import GridView from './grid.js';

describe('GridView interactions', () => {
	let gridView;

	beforeEach(() => {
		document.body.innerHTML = `
			<div id="grid-view">
				<button class="tab-btn active" data-year="1998">1998</button>
				<button class="tab-btn" data-year="1999">1999</button>
				<div id="grid-content-1998"><table><tbody id="grid-table-body"></tbody></table></div>
				<div id="grid-content-1999" style="display:none;"><table><tbody id="grid-table-body-1999"></tbody></table></div>
			</div>
		`;
		gridView = new GridView();
	});

	it('calls year request handler when switching tabs', () => {
		const onYear = vi.fn();
		gridView.setYearRequestHandler(onYear);

		const year1999Btn = document.querySelector('.tab-btn[data-year="1999"]');
		year1999Btn.click();

		expect(onYear).toHaveBeenCalledWith(1999);
		expect(document.getElementById('grid-content-1998').style.display).toBe('none');
		expect(document.getElementById('grid-content-1999').style.display).toBe('block');
	});

	it('calls driver select handler when clicking a driver link', () => {
		const onDriver = vi.fn();
		gridView.setDriverSelectHandler(onDriver);
		gridView.setDriverCountryMap([{ name: 'John Newhouse', country: 'Canada' }]);
		gridView.render([{ Team: 'Warrick', Driver1: 'John Newhouse', Driver2: 'VACANT', TechnicalDirector: 'Peter Heed' }], 1998);

		const link = document.querySelector('.driver-link[data-driver-name="John Newhouse"]');
		expect(link).toBeTruthy();
		link.click();

		expect(onDriver).toHaveBeenCalledWith('John Newhouse');
	});
});
