import { describe, it, expect, beforeEach } from 'vitest';
import GridView from './grid.js';

describe('GridView', () => {
	let gridView;
	let container;

	beforeEach(() => {
		// Setup simple DOM
		document.body.innerHTML = `
            <div id="grid-view">
                <table>
                    <thead></thead>
                    <tbody id="grid-table-body"></tbody>
                </table>
            </div>
        `;
		container = document.getElementById('grid-view');
		gridView = new GridView();
	});

	it('renders grid data correctly', () => {
		const mockData = [
			{ Team: 'Team A', Country: 'UK', Driver1: 'Driver 1', Driver2: 'Driver 2' },
			{ Team: 'Team B', Country: 'IT', Driver1: 'Driver 3', Driver2: 'VACANT' }
		];

		gridView.render(mockData);

		const rows = document.querySelectorAll('#grid-table-body tr');
		expect(rows.length).toBe(2);

		// Check first row content
		const cells1 = rows[0].querySelectorAll('td');
		expect(cells1[0].textContent).toBe('Team A');
		expect(cells1[1].textContent).toBe('Driver 1');
		expect(cells1[2].textContent).toBe('Driver 2');

		// Check second row content
		const cells2 = rows[1].querySelectorAll('td');
		expect(cells2[2].textContent).toBe('VACANT');
	});

	it('handles empty data', () => {
		gridView.render([]);
		const rows = document.querySelectorAll('#grid-table-body tr');
		expect(rows.length).toBe(0);
	});
});
