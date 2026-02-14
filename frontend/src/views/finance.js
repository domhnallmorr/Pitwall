/**
 * Finance View
 * Displays team balance and transaction log.
 */

export default class FinanceView {
	constructor() {
		this.balanceEl = document.getElementById('finance-balance-value');
		this.tbody = document.getElementById('finance-transactions-body');
	}

	render(data) {
		// Update balance display
		const balance = data.balance || 0;
		const formatted = '$' + Math.abs(balance).toLocaleString();
		this.balanceEl.textContent = balance < 0 ? '-' + formatted : formatted;
		this.balanceEl.className = balance < 0
			? 'finance-balance-amount finance-negative'
			: 'finance-balance-amount';

		// Render transactions (most recent first)
		this.tbody.innerHTML = '';
		const transactions = data.transactions || [];
		const reversed = [...transactions].reverse();

		reversed.forEach(t => {
			const row = document.createElement('tr');
			const amountFormatted = '$' + Math.abs(t.amount).toLocaleString();
			const amountClass = t.amount >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
			const amountDisplay = t.amount >= 0 ? '+' + amountFormatted : '-' + amountFormatted;
			const categoryLabel = t.category.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

			row.innerHTML = `
				<td>Week ${t.week}, ${t.year}</td>
				<td>${t.description}</td>
				<td><span class="finance-category-badge">${categoryLabel}</span></td>
				<td class="${amountClass}">${amountDisplay}</td>
			`;
			this.tbody.appendChild(row);
		});

		if (transactions.length === 0) {
			this.tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b;">No transactions yet.</td></tr>';
		}
	}
}
