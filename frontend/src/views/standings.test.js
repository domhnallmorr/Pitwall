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
});
