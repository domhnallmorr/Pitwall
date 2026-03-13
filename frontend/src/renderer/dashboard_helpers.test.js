import { describe, expect, it, vi, beforeEach } from 'vitest';

import {
	handleGameStart,
	openDriverProfile,
	refreshVisibleViews,
	showTeamSelect,
	updateDashboard,
} from './dashboard_helpers.js';

describe('dashboard_helpers', () => {
	beforeEach(() => {
		document.body.innerHTML = `
			<div id="advance-btn"></div>
			<div id="grid-view" style="display:none;"></div>
			<div id="staff-view" style="display:none;"></div>
			<div id="car-view" style="display:none;"></div>
			<div id="standings-view" style="display:none;"></div>
			<div id="driver-view" style="display:none;"></div>
			<div id="finance-view" style="display:none;"></div>
			<div id="facilities-view" style="display:none;"></div>
		`;
	});

	it('handles start and dashboard refresh branches', () => {
		const gridView = { baseYear: 1998, setSeasonBase: vi.fn(), getActiveYear: vi.fn(() => 1998) };
		const api = { getStandings: vi.fn(), getGrid: vi.fn(), getDriver: vi.fn(), getFinance: vi.fn(), getFacilities: vi.fn(), getStaff: vi.fn(), getCar: vi.fn() };
		const emailView = { updateUnreadBadge: vi.fn() };
		const titleScreen = document.createElement('div');
		const dashboard = document.createElement('div');
		const teamNameEl = document.createElement('div');
		const weekEl = document.createElement('div');
		const nextEventEl = document.createElement('div');
		const balanceEl = document.createElement('div');

		handleGameStart({
			data: { team_name: 'Warrick', week_display: 'Week 1', next_event_display: 'Next: A', year: 1998 },
			titleScreen,
			dashboard,
			gridView,
			teamNameEl,
			weekEl,
			nextEventEl,
			balanceEl,
			emailView,
			api,
		});

		expect(titleScreen.style.display).toBe('none');
		expect(dashboard.style.display).toBe('flex');
		expect(emailView.updateUnreadBadge).not.toHaveBeenCalled();

		const advanceBtn = document.getElementById('advance-btn');
		updateDashboard({
			data: {
				new_date_display: 'Week 2',
				next_event_display: 'Next: B',
				button_text: 'GO TO RACE',
				event_active: true,
				year: 1999,
				balance: -1234,
			},
			weekEl,
			nextEventEl,
			balanceEl,
			gridView,
			api,
		});

		expect(advanceBtn.textContent).toBe('GO TO RACE');
		expect(advanceBtn.classList.contains('event-active')).toBe(true);
		expect(gridView.setSeasonBase).toHaveBeenCalledWith(1999);
		expect(api.getGrid).toHaveBeenCalledWith(1999);
		expect(api.getGrid).toHaveBeenCalledWith(2000);
		expect(balanceEl.textContent).toContain('$1,234');
		expect(balanceEl.className).toContain('balance-negative');
	});

	it('shows team select and refreshes visible views including driver profile', () => {
		const titleStartActions = document.createElement('div');
		const teamSelectScreen = document.createElement('div');
		const teamSelectButtons = document.createElement('div');
		const api = {
			startCareer: vi.fn(),
			getGrid: vi.fn(),
			getStaff: vi.fn(),
			getCar: vi.fn(),
			getStandings: vi.fn(),
			getDriver: vi.fn(),
			getFinance: vi.fn(),
			getFacilities: vi.fn(),
		};
		const gridView = { getActiveYear: vi.fn(() => 2001) };
		const driverView = { currentDriverName: 'Driver X' };

		showTeamSelect({
			titleStartActions,
			teamSelectScreen,
			teamSelectButtons,
			teamOptions: ['A', 'B'],
			api,
		});

		expect(titleStartActions.style.display).toBe('none');
		expect(teamSelectScreen.style.display).toBe('block');
		teamSelectButtons.querySelector('button').click();
		expect(api.startCareer).toHaveBeenCalledWith('A');

		document.getElementById('grid-view').style.display = 'block';
		document.getElementById('staff-view').style.display = 'block';
		document.getElementById('car-view').style.display = 'block';
		document.getElementById('standings-view').style.display = 'block';
		document.getElementById('driver-view').style.display = 'block';
		document.getElementById('finance-view').style.display = 'block';
		document.getElementById('facilities-view').style.display = 'block';

		refreshVisibleViews({ gridView, driverView, api });

		expect(api.getGrid).toHaveBeenCalledWith(2001);
		expect(api.getStaff).toHaveBeenCalled();
		expect(api.getCar).toHaveBeenCalled();
		expect(api.getStandings).toHaveBeenCalled();
		expect(api.getDriver).toHaveBeenCalledWith('Driver X');
		expect(api.getFinance).toHaveBeenCalled();
		expect(api.getFacilities).toHaveBeenCalled();
	});

	it('handles guard paths for team select and driver profile', () => {
		const api = { getDriver: vi.fn() };
		showTeamSelect({ titleStartActions: null, teamSelectScreen: null, teamSelectButtons: null, teamOptions: [], api });

		openDriverProfile('', { showView: vi.fn() }, api);
		expect(api.getDriver).not.toHaveBeenCalled();

		openDriverProfile('Driver Y', null, api);
		expect(api.getDriver).toHaveBeenCalledWith('Driver Y');
	});
});
