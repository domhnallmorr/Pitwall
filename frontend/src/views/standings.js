/**
 * Standings View Module
 * Handles Drivers and Constructors standings tables.
 */
import { renderFlagLabel } from './flags.js';

export default class StandingsView {
	constructor() {
		this.driverTableBody = document.getElementById('driver-standings-body');
		this.constructorTableBody = document.getElementById('constructor-standings-body');

		this.tabBtns = document.querySelectorAll('.standings-tab-btn');
		this.driverContent = document.getElementById('standings-content-drivers');
		this.constructorContent = document.getElementById('standings-content-constructors');

		this.initTabs();
	}

	initTabs() {
		this.tabBtns.forEach(btn => {
			btn.addEventListener('click', () => {
				this.setActiveTab(btn);
				this.toggleContent(btn.getAttribute('data-type'));
			});
		});
	}

	setActiveTab(targetBtn) {
		this.tabBtns.forEach(b => b.classList.remove('active'));
		targetBtn.classList.add('active');
	}

	toggleContent(type) {
		if (type === 'drivers') {
			this.driverContent.style.display = 'block';
			this.constructorContent.style.display = 'none';
		} else {
			this.driverContent.style.display = 'none';
			this.constructorContent.style.display = 'block';
		}
	}

	render(data) {
		this.renderDrivers(data.drivers);
		this.renderConstructors(data.constructors);
	}

	renderDrivers(drivers) {
		this.driverTableBody.innerHTML = '';
		drivers.forEach((driver, index) => {
			const tr = document.createElement('tr');
			tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${renderFlagLabel(driver.country, driver.name)}</td>
                <td>${driver.points}</td>
            `;
			this.driverTableBody.appendChild(tr);
		});
	}

	renderConstructors(teams) {
		this.constructorTableBody.innerHTML = '';
		teams.forEach((team, index) => {
			const tr = document.createElement('tr');
			tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${renderFlagLabel(team.country, team.name)}</td>
                <td>${team.points}</td>
            `;
			this.constructorTableBody.appendChild(tr);
		});
	}
}
