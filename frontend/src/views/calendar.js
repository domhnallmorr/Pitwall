export default class CalendarView {
	constructor() {
		this.view = document.getElementById('calendar-view');
		this.tableBody = document.getElementById('calendar-table-body');
		this.filterSelect = document.getElementById('calendar-filter');

		this.allData = []; // Store full dataset

		this.initListeners();
	}

	initListeners() {
		this.filterSelect.addEventListener('change', () => {
			this.applyFilter();
		});
	}

	render(data) {
		this.allData = data || [];
		this.applyFilter();
	}

	applyFilter() {
		const filterValue = this.filterSelect.value;

		let filteredData = this.allData;
		if (filterValue !== 'all') {
			filteredData = this.allData.filter(event => event.type === filterValue);
		}

		this.renderTable(filteredData);
	}

	renderTable(data) {
		this.tableBody.innerHTML = '';

		if (!data || data.length === 0) {
			this.tableBody.innerHTML = '<tr><td colspan="6">No events found.</td></tr>';
			return;
		}

		data.forEach(event => {
			const row = document.createElement('tr');

			// Highlight testing rows
			if (event.type === 'Test') {
				row.classList.add('test-session-row');
				row.style.opacity = '0.7';
			}

			row.innerHTML = `
                <td>${event.round}</td>
                <td>${event.week}</td>
                <td>${event.type}</td>
                <td>${event.track}</td>
                <td>${event.country}</td>
                <td>${event.winner}</td>
            `;
			this.tableBody.appendChild(row);
		});
	}
}
