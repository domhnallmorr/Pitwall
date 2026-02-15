/**
 * Grid View Module
 * Handles Grid table rendering and tab logic.
 */
import { renderFlagLabel } from './flags.js';

export default class GridView {
	constructor() {
		this.view = document.getElementById('grid-view');
		this.tableBody = document.getElementById('grid-table-body');
		this.tableBodyNext = document.getElementById('grid-table-body-1999');
		this.tabBtns = this.view ? this.view.querySelectorAll('.tab-btn[data-year]') : [];
		this.content1998 = document.getElementById('grid-content-1998');
		this.content1999 = document.getElementById('grid-content-1999');
		this.baseYear = 1998;
		this.requestYearData = null;
		this.driverCountryByName = {};

		this.initTabs();
	}

	setSeasonBase(year) {
		this.baseYear = Number(year) || this.baseYear;
		const years = [this.baseYear, this.baseYear + 1];

		this.tabBtns.forEach((btn, idx) => {
			const y = years[idx];
			btn.setAttribute('data-year', String(y));
			btn.textContent = String(y);
		});

		// Keep first tab active by default when season changes.
		const first = this.tabBtns[0];
		if (first) {
			this.setActiveTab(first);
			this.toggleContent(first.getAttribute('data-year'));
		}
	}

	setYearRequestHandler(handler) {
		this.requestYearData = handler;
	}

	setDriverCountryMap(drivers) {
		const map = {};
		(drivers || []).forEach((d) => {
			if (d && d.name) {
				map[d.name] = d.country || '';
			}
		});
		this.driverCountryByName = map;
	}

	getActiveYear() {
		const active = this.view ? this.view.querySelector('.tab-btn[data-year].active') : null;
		return active ? Number(active.getAttribute('data-year')) : this.baseYear;
	}

	initTabs() {
		this.tabBtns.forEach(btn => {
			btn.addEventListener('click', () => {
				this.setActiveTab(btn);
				const year = btn.getAttribute('data-year');
				this.toggleContent(year);
				if (this.requestYearData) {
					this.requestYearData(Number(year));
				}
			});
		});
	}

	setActiveTab(targetBtn) {
		this.tabBtns.forEach(b => b.classList.remove('active'));
		targetBtn.classList.add('active');
	}

	toggleContent(year) {
		if (Number(year) === this.baseYear) {
			this.content1998.style.display = 'block';
			this.content1999.style.display = 'none';
		} else {
			this.content1998.style.display = 'none';
			this.content1999.style.display = 'block';
		}
	}

	render(data, year) {
		const targetYear = Number.isFinite(Number(year)) ? Number(year) : this.getActiveYear();
		const isCurrentTab = targetYear === this.baseYear;
		const targetBody = isCurrentTab ? this.tableBody : this.tableBodyNext;
		if (!targetBody) return;

		targetBody.innerHTML = ''; // Clear existing
		data.forEach(row => {
			const d1Name = row.Driver1 || 'Vacant';
			const d2Name = row.Driver2 || 'Vacant';
			const d1Country = this.driverCountryByName[d1Name] || '';
			const d2Country = this.driverCountryByName[d2Name] || '';

			const tr = document.createElement('tr');
			tr.innerHTML = `
                <td>${row.Team}</td>
                <td>${renderFlagLabel(d1Country, d1Name)}</td>
                <td>${renderFlagLabel(d2Country, d2Name)}</td>
            `;
			targetBody.appendChild(tr);
		});
	}
}
