import { describe, it, expect, beforeEach, vi } from 'vitest';
import StandingsView from './standings.js';

describe('StandingsView', () => {
	let standingsView;

	beforeEach(() => {
		document.body.innerHTML = `
			<div id="standings-view">
				<button class="standings-tab-btn active" data-type="drivers">Drivers</button>
				<button class="standings-tab-btn" data-type="constructors">Constructors</button>
				<div id="standings-content-drivers" style="display:block;">
					<table><tbody id="driver-standings-body"></tbody></table>
				</div>
				<div id="standings-content-constructors" style="display:none;">
					<table><tbody id="constructor-standings-body"></tbody></table>
				</div>
			</div>
		`;
		standingsView = new StandingsView();
	});

	it('renders drivers and invokes handler when clicking a driver', () => {
		const onDriver = vi.fn();
		standingsView.setDriverSelectHandler(onDriver);
		standingsView.render({
			drivers: [{ name: 'John Newhouse', country: 'Canada', points: 10 }],
			constructors: [],
		});

		const link = document.querySelector('.driver-link[data-driver-name="John Newhouse"]');
		expect(link).toBeTruthy();
		link.click();

		expect(onDriver).toHaveBeenCalledWith('John Newhouse');
	});

	it('toggles to constructors tab content', () => {
		const constructorsBtn = document.querySelector('.standings-tab-btn[data-type="constructors"]');
		constructorsBtn.click();

		expect(document.getElementById('standings-content-drivers').style.display).toBe('none');
		expect(document.getElementById('standings-content-constructors').style.display).toBe('block');
	});

	it('renders constructors and toggles back to drivers tab', () => {
		standingsView.render({
			drivers: [{ name: 'Driver A', country: 'UK', points: 12 }],
			constructors: [{ name: 'Team A', country: 'Italy', points: 20 }],
		});

		expect(document.getElementById('constructor-standings-body').textContent).toContain('Team A');

		const constructorsBtn = document.querySelector('.standings-tab-btn[data-type="constructors"]');
		const driversBtn = document.querySelector('.standings-tab-btn[data-type="drivers"]');
		constructorsBtn.click();
		driversBtn.click();

		expect(document.getElementById('standings-content-drivers').style.display).toBe('block');
		expect(document.getElementById('standings-content-constructors').style.display).toBe('none');
		expect(driversBtn.classList.contains('active')).toBe(true);
	});

	it('clicking a driver without a handler does nothing', () => {
		standingsView.render({
			drivers: [{ name: 'No Handler Driver', country: 'France', points: 3 }],
			constructors: [],
		});

		const link = document.querySelector('.driver-link[data-driver-name="No Handler Driver"]');
		expect(() => link.click()).not.toThrow();
	});
});
