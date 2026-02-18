import { describe, it, expect, beforeEach, vi } from 'vitest';

const { apiMock } = vi.hoisted(() => ({
	apiMock: {
		getEmails: vi.fn(),
		getCalendar: vi.fn(),
		getStandings: vi.fn(),
		getGrid: vi.fn(),
		getStaff: vi.fn(),
		getCar: vi.fn(),
		getFinance: vi.fn(),
		getFacilities: vi.fn(),
	},
}));

vi.mock('../api.js', () => ({ default: apiMock }));

import Navigation from './navigation.js';

describe('Navigation', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		document.body.innerHTML = `
			<div class="sidebar">
				<button class="nav-item active">Home</button>
				<button class="nav-item">Email</button>
				<button class="nav-item">Calendar</button>
				<button class="nav-item">Grid</button>
				<button class="nav-item">Staff</button>
				<button class="nav-item">Car</button>
				<button class="nav-item">Finance</button>
				<button class="nav-item">Facilities</button>
				<button class="nav-item">Standings</button>
			</div>
			<div id="home-view" style="display:block;"></div>
			<div id="email-view" style="display:none;"></div>
			<div id="calendar-view" style="display:none;"></div>
			<div id="grid-view" style="display:none;">
				<button class="tab-btn active" data-year="1998">1998</button>
			</div>
			<div id="staff-view" style="display:none;"></div>
			<div id="driver-view" style="display:none;"></div>
			<div id="car-view" style="display:none;"></div>
			<div id="finance-view" style="display:none;"></div>
			<div id="facilities-view" style="display:none;"></div>
			<div id="standings-view" style="display:none;"></div>
		`;
		new Navigation();
	});

	it('navigates to finance and requests finance data', () => {
		const financeBtn = document.querySelectorAll('.nav-item')[6];
		financeBtn.click();

		expect(apiMock.getFinance).toHaveBeenCalledTimes(1);
		expect(document.getElementById('finance-view').style.display).toBe('block');
	});

	it('navigates to standings and requests standings data', () => {
		const standingsBtn = document.querySelectorAll('.nav-item')[8];
		standingsBtn.click();

		expect(apiMock.getStandings).toHaveBeenCalledTimes(1);
		expect(document.getElementById('standings-view').style.display).toBe('block');
	});

	it('navigates to email and requests email data', () => {
		const btn = document.querySelectorAll('.nav-item')[1];
		btn.click();
		expect(apiMock.getEmails).toHaveBeenCalledTimes(1);
		expect(document.getElementById('email-view').style.display).toBe('block');
	});

	it('navigates to calendar and requests calendar data', () => {
		const btn = document.querySelectorAll('.nav-item')[2];
		btn.click();
		expect(apiMock.getCalendar).toHaveBeenCalledTimes(1);
		expect(document.getElementById('calendar-view').style.display).toBe('block');
	});

	it('navigates to grid and requests standings + grid for active year', () => {
		const btn = document.querySelectorAll('.nav-item')[3];
		btn.click();
		expect(apiMock.getStandings).toHaveBeenCalledTimes(1);
		expect(apiMock.getGrid).toHaveBeenCalledWith(1998);
		expect(document.getElementById('grid-view').style.display).toBe('block');
	});

	it('navigates to staff and requests staff data', () => {
		const btn = document.querySelectorAll('.nav-item')[4];
		btn.click();
		expect(apiMock.getStaff).toHaveBeenCalledTimes(1);
		expect(document.getElementById('staff-view').style.display).toBe('block');
	});

	it('navigates to car and requests car data', () => {
		const btn = document.querySelectorAll('.nav-item')[5];
		btn.click();
		expect(apiMock.getCar).toHaveBeenCalledTimes(1);
		expect(document.getElementById('car-view').style.display).toBe('block');
	});

	it('navigates to facilities and requests facilities data', () => {
		const btn = document.querySelectorAll('.nav-item')[7];
		btn.click();
		expect(apiMock.getFacilities).toHaveBeenCalledTimes(1);
		expect(document.getElementById('facilities-view').style.display).toBe('block');
	});

	it('navigates to home without API requests', () => {
		const btn = document.querySelectorAll('.nav-item')[0];
		btn.click();
		expect(apiMock.getEmails).not.toHaveBeenCalled();
		expect(document.getElementById('home-view').style.display).toBe('block');
	});
});
