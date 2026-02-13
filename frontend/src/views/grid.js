/**
 * Grid View Module
 * Handles Grid table rendering and tab logic.
 */

export default class GridView {
	constructor() {
		this.tableBody = document.getElementById('grid-table-body');
		this.tabBtns = document.querySelectorAll('.tab-btn');
		this.content1998 = document.getElementById('grid-content-1998');
		this.content1999 = document.getElementById('grid-content-1999');

		this.initTabs();
	}

	initTabs() {
		this.tabBtns.forEach(btn => {
			btn.addEventListener('click', () => {
				this.setActiveTab(btn);
				this.toggleContent(btn.getAttribute('data-year'));
			});
		});
	}

	setActiveTab(targetBtn) {
		this.tabBtns.forEach(b => b.classList.remove('active'));
		targetBtn.classList.add('active');
	}

	toggleContent(year) {
		if (year === '1998') {
			this.content1998.style.display = 'block';
			this.content1999.style.display = 'none';
		} else {
			this.content1998.style.display = 'none';
			this.content1999.style.display = 'block';
		}
	}

	render(data) {
		this.tableBody.innerHTML = ''; // Clear existing

		data.forEach(row => {
			const tr = document.createElement('tr');
			tr.innerHTML = `
                <td>${row.Team}</td>
                <td>${row.Driver1 || 'Vacant'}</td>
                <td>${row.Driver2 || 'Vacant'}</td>
            `;
			this.tableBody.appendChild(tr);
		});
	}
}
