/**
 * Navigation Module
 * Handles sidebar interaction and view switching.
 */

import API from '../api.js';

export default class Navigation {
	constructor() {
		this.navItems = document.querySelectorAll('.nav-item');
		this.views = {
			'home': document.getElementById('home-view'),
			'email': document.getElementById('email-view'),
			'calendar': document.getElementById('calendar-view'),
			'grid': document.getElementById('grid-view'),
			'staff': document.getElementById('staff-view'),
			'standings': document.getElementById('standings-view')
		};

		this.initListeners();
	}

	initListeners() {
		this.navItems.forEach((item, index) => {
			item.addEventListener('click', () => {
				this.setActive(item);
				this.handleNavigation(index);
			});
		});
	}

	setActive(targetItem) {
		this.navItems.forEach(n => n.classList.remove('active'));
		targetItem.classList.add('active');
	}

	handleNavigation(index) {
		// 0: Home, 1: Email, 2: Calendar, 3: Grid, 4: Staff, 5: Standings
		if (index === 0) { // Home
			this.showView('home');
		} else if (index === 1) { // Email
			this.showView('email');
			console.log("Requesting Email Data...");
			API.getEmails();
		} else if (index === 2) { // Calendar
			this.showView('calendar');
			console.log("Requesting Calendar Data...");
			API.getCalendar();
		} else if (index === 3) { // Grid
			this.showView('grid');
			console.log("Requesting Grid Data...");
			API.getGrid();
		} else if (index === 4) { // Staff
			this.showView('staff');
			console.log("Requesting Staff Data...");
			API.getStaff();
		} else if (index === 5) { // Standings
			this.showView('standings');
			console.log("Requesting Standings Data...");
			API.getStandings();
		} else {
			console.log("Navigating to placeholder...");
		}
	}

	showView(viewName) {
		Object.values(this.views).forEach(v => v.style.display = 'none');
		if (this.views[viewName]) {
			this.views[viewName].style.display = 'block';
		}
	}
}
