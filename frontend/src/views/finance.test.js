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
			<div id="finance-engine-supplier-total"></div>
			<div id="finance-tyre-supplier-total"></div>
			<div id="finance-sponsorship-total"></div>
			<div id="finance-prize-progress"></div>
			<div id="finance-sponsor-name"></div>
			<div id="finance-sponsor-annual"></div>
			<div id="finance-sponsor-installment"></div>
			<div id="finance-sponsor-paid"></div>
			<div id="finance-sponsor-remaining"></div>
			<div id="finance-sponsor-logo-wrap"></div>
			<div id="finance-engine-supplier-name"></div>
			<div id="finance-engine-supplier-deal"></div>
			<div id="finance-engine-supplier-annual"></div>
			<div id="finance-engine-supplier-installment"></div>
			<div id="finance-engine-supplier-paid"></div>
			<div id="finance-engine-supplier-remaining"></div>
			<div id="finance-engine-supplier-logo-wrap"></div>
			<div id="finance-tyre-supplier-name"></div>
			<div id="finance-tyre-supplier-deal"></div>
			<div id="finance-tyre-supplier-annual"></div>
			<div id="finance-tyre-supplier-installment"></div>
			<div id="finance-tyre-supplier-paid"></div>
			<div id="finance-tyre-supplier-remaining"></div>
			<div id="finance-tyre-supplier-logo-wrap"></div>
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
				workforce_total: 700,
				engine_supplier_total: 281250,
				tyre_supplier_total: 0,
				sponsorship_total: 900
			},
			sponsor: {
				name: 'Windale',
				annual_value: 32500000,
				installment: 2031250,
				paid_so_far: 2031250,
				remaining: 30468750,
			},
			engine_supplier: {
				name: 'Mechatron',
				deal: 'customer',
				annual_value: 4500000,
				installment: 281250,
				paid_so_far: 281250,
				remaining: 4218750,
			},
			tyre_supplier: {
				name: 'Greatday',
				deal: 'partner',
				annual_value: 0,
				installment: 0,
				paid_so_far: 0,
				remaining: 0,
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
		expect(document.getElementById('finance-engine-supplier-total').textContent).toBe('$281,250')
		expect(document.getElementById('finance-tyre-supplier-total').textContent).toBe('$0')
		expect(document.getElementById('finance-sponsorship-total').textContent).toBe('$900')
		expect(document.getElementById('finance-sponsor-name').textContent).toBe('Windale')
		expect(document.getElementById('finance-engine-supplier-name').textContent).toBe('Mechatron')
		expect(document.getElementById('finance-engine-supplier-deal').textContent).toBe('customer')
		expect(document.getElementById('finance-tyre-supplier-name').textContent).toBe('Greatday')
		const trackRows = document.querySelectorAll('#finance-track-pl-body tr')
		expect(trackRows.length).toBe(1)
		expect(trackRows[0].innerHTML).toContain('Albert Park')
		const txRows = document.querySelectorAll('#finance-transactions-body tr')
		expect(txRows.length).toBe(1)
		expect(txRows[0].innerHTML).toContain('Transport')
	})
})
