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
		this.headCurrent = document.getElementById('grid-head-1998');
		this.headNext = document.getElementById('grid-head-1999');
		this.modeToggle = document.getElementById('grid-mode-toggle');
		this.tabBtns = this.view ? this.view.querySelectorAll('.tab-btn[data-year]') : [];
		this.content1998 = document.getElementById('grid-content-1998');
		this.content1999 = document.getElementById('grid-content-1999');
		this.baseYear = 1998;
		this.requestYearData = null;
		this.driverCountryByName = {};
		this.onDriverSelected = null;
		this.mode = 'staff';
		this.yearData = new Map();

		this.initTabs();
		this.initModeToggle();
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

	setDriverSelectHandler(handler) {
		this.onDriverSelected = handler;
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
				this.renderYear(Number(year));
			});
		});
	}

	initModeToggle() {
		if (!this.modeToggle) return;
		this.modeToggle.addEventListener('change', () => {
			const selected = this.modeToggle.value;
			this.mode = selected === 'sponsors' || selected === 'suppliers' ? selected : 'staff';
			this.renderYear(this.getActiveYear(), true);
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
			this.playTabTransition(this.content1998);
		} else {
			this.content1998.style.display = 'none';
			this.content1999.style.display = 'block';
			this.playTabTransition(this.content1999);
		}
	}

	playTabTransition(contentEl) {
		if (!contentEl) return;
		contentEl.classList.remove('grid-tab-enter');
		// Force reflow so rapid repeated tab clicks replay animation.
		void contentEl.offsetWidth;
		contentEl.classList.add('grid-tab-enter');
	}

	render(data, year) {
		const targetYear = Number.isFinite(Number(year)) ? Number(year) : this.getActiveYear();
		this.yearData.set(targetYear, Array.isArray(data) ? data : []);
		this.renderYear(targetYear);
	}

	renderYear(targetYear, animate = false) {
		const isCurrentTab = targetYear === this.baseYear;
		const targetBody = isCurrentTab ? this.tableBody : this.tableBodyNext;
		const targetHead = isCurrentTab ? this.headCurrent : this.headNext;
		const targetContent = isCurrentTab ? this.content1998 : this.content1999;
		if (!targetBody) return;
		const data = this.yearData.get(targetYear) || [];

			if (targetHead) {
			if (this.mode === 'sponsors') {
				targetHead.innerHTML = '<tr><th>Team</th><th>Title Sponsor</th></tr>';
			} else if (this.mode === 'suppliers') {
				targetHead.innerHTML = '<tr><th>Team</th><th>Engine Supplier</th><th>Deal</th></tr>';
			} else {
				targetHead.innerHTML = '<tr><th>Team</th><th>Driver 1</th><th>Driver 2</th><th>Technical Director</th><th>Commercial Manager</th></tr>';
			}
		}

		targetBody.innerHTML = ''; // Clear existing
		data.forEach(row => {
			const tr = document.createElement('tr');
			if (this.mode === 'sponsors') {
				const sponsorName = row.TitleSponsor || 'VACANT';
				tr.innerHTML = `
					<td>${row.Team}</td>
					<td>${this.renderSponsorCell(sponsorName)}</td>
				`;
			} else if (this.mode === 'suppliers') {
				const supplierName = row.EngineSupplier || 'VACANT';
				const supplierCountry = row.EngineSupplierCountry || '';
				const supplierDealRaw = row.EngineSupplierDeal || '-';
				const supplierDeal = supplierDealRaw === '-'
					? supplierDealRaw
					: supplierDealRaw.charAt(0).toUpperCase() + supplierDealRaw.slice(1).toLowerCase();
				tr.innerHTML = `
					<td>${row.Team}</td>
					<td>${this.renderStaffCell(supplierCountry, supplierName)}</td>
					<td>${supplierDeal}</td>
				`;
			} else {
				const d1Name = row.Driver1 || 'Vacant';
				const d2Name = row.Driver2 || 'Vacant';
				const tdName = row.TechnicalDirector || 'VACANT';
				const d1Country = this.driverCountryByName[d1Name] || '';
				const d2Country = this.driverCountryByName[d2Name] || '';
				const tdCountry = row.TechnicalDirectorCountry || '';
				const cmName = row.CommercialManager || 'VACANT';
				tr.innerHTML = `
	                <td>${row.Team}</td>
	                <td>${this.renderDriverCell(d1Country, d1Name)}</td>
	                <td>${this.renderDriverCell(d2Country, d2Name)}</td>
	                <td>${this.renderStaffCell(tdCountry, tdName)}</td>
	                <td>${this.renderStaffCell('', cmName)}</td>
	            `;
			}
			targetBody.appendChild(tr);
		});

		if (this.mode === 'staff') {
			targetBody.querySelectorAll('.driver-link').forEach((btn) => {
				btn.addEventListener('click', () => {
					if (this.onDriverSelected) {
						this.onDriverSelected(btn.getAttribute('data-driver-name'));
					}
				});
			});
		}

		if (animate && targetContent) {
			this.playTabTransition(targetContent);
		}
	}

	renderDriverCell(country, name) {
		if (!name || name === 'VACANT' || name === 'Vacant') {
			return name || 'VACANT';
		}
		return `<button class="driver-link" data-driver-name="${name}">${renderFlagLabel(country, name)}</button>`;
	}

	renderStaffCell(country, name) {
		if (!name || name === 'VACANT' || name === 'Vacant') {
			return name || 'VACANT';
		}
		return renderFlagLabel(country, name);
	}

	renderSponsorCell(name) {
		if (!name || name === 'VACANT' || name === 'Vacant') {
			return 'VACANT';
		}
		const encodedOriginal = encodeURIComponent(name);
		const encodedLower = encodeURIComponent(name.toLowerCase());
		const encodedUpper = encodeURIComponent(name.toUpperCase());
		return `
			<span class="sponsor-label">
				<img class="sponsor-logo" src="assets/sponsor_logos/${encodedOriginal}.png" alt="${name} logo"
					onerror="if(!this.dataset.f1){this.dataset.f1='1';this.src='assets/sponsor_logos/${encodedLower}.png';}else if(!this.dataset.f2){this.dataset.f2='1';this.src='assets/sponsor_logos/${encodedUpper}.png';}else{this.style.display='none';}">
				<span>${name}</span>
			</span>
		`;
	}
}
