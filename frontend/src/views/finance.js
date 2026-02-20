/**
 * Finance View
 * Displays team balance and transaction log.
 */

export default class FinanceView {
	constructor() {
		this.balanceEl = document.getElementById('finance-balance-value');
		this.prizeEntitlementEl = document.getElementById('finance-prize-entitlement');
		this.prizePaidEl = document.getElementById('finance-prize-paid');
		this.prizeRemainingEl = document.getElementById('finance-prize-remaining');
		this.incomeTotalEl = document.getElementById('finance-income-total');
		this.expenseTotalEl = document.getElementById('finance-expense-total');
		this.netPlEl = document.getElementById('finance-net-pl');
		this.transportTotalEl = document.getElementById('finance-transport-total');
		this.workforceTotalEl = document.getElementById('finance-workforce-total');
		this.prizeProgressEl = document.getElementById('finance-prize-progress');
		this.trackPlBody = document.getElementById('finance-track-pl-body');
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

		const entitlement = data.prize_money_entitlement || 0;
		const paid = data.prize_money_paid || 0;
		const remaining = data.prize_money_remaining || 0;
		const racesPaid = data.prize_money_races_paid || 0;
		const totalRaces = data.prize_money_total_races || 0;

		if (this.prizeEntitlementEl) this.prizeEntitlementEl.textContent = '$' + entitlement.toLocaleString();
		if (this.prizePaidEl) this.prizePaidEl.textContent = '$' + paid.toLocaleString();
		if (this.prizeRemainingEl) this.prizeRemainingEl.textContent = '$' + remaining.toLocaleString();
		if (this.prizeProgressEl) this.prizeProgressEl.textContent = `Race installments: ${racesPaid} / ${totalRaces}`;

		const summary = data.summary || {};
		const incomeTotal = summary.income_total || 0;
		const expenseTotal = summary.expense_total || 0;
		const netPl = summary.net_profit_loss || 0;
		const transportTotal = summary.transport_total || 0;
		const workforceTotal = summary.workforce_total || 0;

		if (this.incomeTotalEl) this.incomeTotalEl.textContent = '$' + incomeTotal.toLocaleString();
		if (this.expenseTotalEl) this.expenseTotalEl.textContent = '$' + expenseTotal.toLocaleString();
		if (this.transportTotalEl) this.transportTotalEl.textContent = '$' + transportTotal.toLocaleString();
		if (this.workforceTotalEl) this.workforceTotalEl.textContent = '$' + workforceTotal.toLocaleString();
		if (this.netPlEl) {
			const netFormatted = '$' + Math.abs(netPl).toLocaleString();
			this.netPlEl.textContent = netPl < 0 ? '-' + netFormatted : netFormatted;
			this.netPlEl.className = netPl < 0
				? 'finance-balance-amount finance-negative'
				: 'finance-balance-amount';
		}

		// Track P/L table
		if (this.trackPlBody) {
			this.trackPlBody.innerHTML = '';
			const trackRows = data.track_profit_loss || [];
			trackRows.forEach(rowData => {
				const row = document.createElement('tr');
				const netClass = rowData.net >= 0 ? 'finance-amount-positive' : 'finance-amount-negative';
				row.innerHTML = `
					<td>${rowData.track}</td>
					<td>${rowData.country}</td>
					<td class="finance-amount-positive">$${(rowData.income || 0).toLocaleString()}</td>
					<td class="finance-amount-negative">$${(rowData.expense || 0).toLocaleString()}</td>
					<td class="${netClass}">${rowData.net >= 0 ? '+' : '-'}$${Math.abs(rowData.net || 0).toLocaleString()}</td>
				`;
				this.trackPlBody.appendChild(row);
			});

			if (trackRows.length === 0) {
				this.trackPlBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b;">No track-linked finance yet.</td></tr>';
			}
		}

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
			const categoryClass = t.category === 'transport' ? 'finance-category-badge finance-category-transport' : 'finance-category-badge';

			row.innerHTML = `
				<td>Week ${t.week}, ${t.year}</td>
				<td>${t.description}</td>
				<td><span class="${categoryClass}">${categoryLabel}</span></td>
				<td class="${amountClass}">${amountDisplay}</td>
			`;
			this.tbody.appendChild(row);
		});

		if (transactions.length === 0) {
			this.tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b;">No transactions yet.</td></tr>';
		}
	}
}
