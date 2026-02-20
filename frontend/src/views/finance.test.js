import { describe, it, expect, beforeEach } from 'vitest'
import { JSDOM } from 'jsdom'
import FinanceView from './finance.js'

describe('FinanceView', () => {
	let financeView

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="finance-balance-value"></div>
			<div id="finance-prize-entitlement"></div>
			<div id="finance-prize-paid"></div>
			<div id="finance-prize-remaining"></div>
			<div id="finance-income-total"></div>
			<div id="finance-expense-total"></div>
			<div id="finance-net-pl"></div>
			<div id="finance-transport-total"></div>
			<div id="finance-workforce-total"></div>
			<div id="finance-prize-progress"></div>
			<table><tbody id="finance-track-pl-body"></tbody></table>
			<table><tbody id="finance-transactions-body"></tbody></table>
		`)
		global.document = dom.window.document
		global.window = dom.window
		financeView = new FinanceView()
	})

	it('renders summary totals and track profit/loss rows', () => {
		financeView.render({
			balance: 1000,
			prize_money_entitlement: 3000,
			prize_money_paid: 1000,
			prize_money_remaining: 2000,
			prize_money_races_paid: 1,
			prize_money_total_races: 10,
			summary: {
				income_total: 5000,
				expense_total: 1200,
				net_profit_loss: 3800,
				transport_total: 400,
				workforce_total: 700
			},
			track_profit_loss: [
				{ track: 'Albert Park', country: 'Australia', income: 5000, expense: 400, net: 4600 }
			],
			transactions: [
				{ week: 10, year: 1998, amount: -400, category: 'transport', description: 'Transport to Albert Park' }
			]
		})

		expect(document.getElementById('finance-income-total').textContent).toBe('$5,000')
		expect(document.getElementById('finance-transport-total').textContent).toBe('$400')
		expect(document.getElementById('finance-workforce-total').textContent).toBe('$700')
		const trackRows = document.querySelectorAll('#finance-track-pl-body tr')
		expect(trackRows.length).toBe(1)
		expect(trackRows[0].innerHTML).toContain('Albert Park')
		const txRows = document.querySelectorAll('#finance-transactions-body tr')
		expect(txRows.length).toBe(1)
		expect(txRows[0].innerHTML).toContain('Transport')
	})
})
