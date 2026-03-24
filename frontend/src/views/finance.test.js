import { describe, it, expect, beforeEach, vi } from 'vitest'
import { JSDOM } from 'jsdom'
import FinanceView from './finance.js'

describe('FinanceView', () => {
	let financeView

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="finance-view">
				<button class="finance-tab-btn active" data-type="main"></button>
				<button class="finance-tab-btn" data-type="tracker"></button>
				<button class="finance-tab-btn" data-type="log"></button>
			</div>
			<div id="finance-content-main"></div>
			<div id="finance-content-tracker" style="display:none;"></div>
			<div id="finance-content-log" style="display:none;"></div>
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
			<div id="finance-fuel-supplier-total"></div>
			<div id="finance-sponsorship-total"></div>
			<div id="finance-prize-progress"></div>
			<div id="finance-sponsor-name"></div>
			<button id="finance-sponsor-replace-btn"></button>
			<div id="finance-sponsor-annual"></div>
			<div id="finance-sponsor-installment"></div>
			<div id="finance-sponsor-paid"></div>
			<div id="finance-sponsor-remaining"></div>
			<div id="finance-sponsor-logo-wrap"></div>
			<div id="finance-other-sponsorship-name"></div>
			<div id="finance-other-sponsorship-annual"></div>
			<div id="finance-other-sponsorship-installment"></div>
			<div id="finance-other-sponsorship-paid"></div>
			<div id="finance-other-sponsorship-remaining"></div>
			<div id="finance-other-sponsorship-logo-wrap"></div>
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
			<div id="finance-fuel-supplier-name"></div>
			<div id="finance-fuel-supplier-deal"></div>
			<div id="finance-fuel-supplier-annual"></div>
			<div id="finance-fuel-supplier-installment"></div>
			<div id="finance-fuel-supplier-paid"></div>
			<div id="finance-fuel-supplier-remaining"></div>
			<div id="finance-fuel-supplier-logo-wrap"></div>
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
				fuel_supplier_total: -75000,
				sponsorship_total: 900
			},
			sponsor: {
				name: 'Windale',
				contract_length: 1,
				annual_value: 32500000,
				installment: 2031250,
				paid_so_far: 2031250,
				remaining: 30468750,
			},
			other_sponsorship: {
				annual_value: 9500000,
				installment: 593750,
				paid_so_far: 593750,
				remaining: 8906250,
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
			fuel_supplier: {
				name: 'Brasoil',
				deal: 'partner',
				annual_value: 150000,
				installment: 9375,
				paid_so_far: 9375,
				remaining: 140625,
				direction: 'expense',
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
		expect(document.getElementById('finance-fuel-supplier-total').textContent).toBe('-$75,000')
		expect(document.getElementById('finance-sponsorship-total').textContent).toBe('$900')
		expect(document.getElementById('finance-sponsor-name').textContent).toBe('Windale')
		expect(document.getElementById('finance-sponsor-replace-btn').disabled).toBe(false)
		expect(document.getElementById('finance-other-sponsorship-annual').textContent).toBe('$9,500,000')
		expect(document.getElementById('finance-engine-supplier-name').textContent).toBe('Mechatron')
		expect(document.getElementById('finance-engine-supplier-deal').textContent).toBe('customer')
		expect(document.getElementById('finance-tyre-supplier-name').textContent).toBe('Greatday')
		expect(document.getElementById('finance-fuel-supplier-name').textContent).toBe('Brasoil')
		expect(document.getElementById('finance-fuel-supplier-annual').textContent).toBe('-$150,000')
		const trackRows = document.querySelectorAll('#finance-track-pl-body tr')
		expect(trackRows.length).toBe(1)
		expect(trackRows[0].innerHTML).toContain('Albert Park')
		const txRows = document.querySelectorAll('#finance-transactions-body tr')
		expect(txRows.length).toBe(1)
		expect(txRows[0].innerHTML).toContain('Transport')
	})

	it('handles tab switching, empty states, and logo reset branches', () => {
		financeView.render({
			balance: -100,
			summary: {
				income_total: 0,
				expense_total: 0,
				net_profit_loss: -100,
				transport_total: 0,
				workforce_total: 0,
				engine_supplier_total: 0,
				tyre_supplier_total: 0,
				fuel_supplier_total: 10,
				sponsorship_total: 0
			},
			sponsor: { name: null, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			other_sponsorship: { annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			engine_supplier: { name: null, deal: '-', annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			tyre_supplier: { name: null, deal: '-', annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			fuel_supplier: { name: null, deal: '-', annual_value: -1000, installment: 50, paid_so_far: 0, remaining: 950, direction: 'income' },
			track_profit_loss: [],
			transactions: []
		})

		expect(document.getElementById('finance-balance-value').textContent).toBe('-$100')
		expect(document.getElementById('finance-fuel-supplier-total').textContent).toBe('+$10')
		expect(document.getElementById('finance-fuel-supplier-installment').textContent).toBe('+$50')
		expect(document.getElementById('finance-track-pl-body').textContent).toContain('No track-linked finance yet')
		expect(document.getElementById('finance-transactions-body').textContent).toContain('No transactions yet')
		expect(document.getElementById('finance-sponsor-logo-wrap').innerHTML).toBe('')
		expect(document.getElementById('finance-sponsor-replace-btn').disabled).toBe(true)
		expect(document.getElementById('finance-engine-supplier-logo-wrap').innerHTML).toBe('')

		const trackerBtn = document.querySelector('.finance-tab-btn[data-type="tracker"]')
		trackerBtn.click()
		expect(document.getElementById('finance-content-main').style.display).toBe('none')
		expect(document.getElementById('finance-content-tracker').style.display).toBe('block')
	})

	it('triggers title sponsor replace handler when enabled', () => {
		const onReplace = vi.fn()
		financeView.setReplaceTitleSponsorHandler(onReplace)
		financeView.render({
			balance: 0,
			summary: {},
			sponsor: { name: 'Windale', contract_length: 1, annual_value: 1, installment: 0, paid_so_far: 0, remaining: 1 },
			other_sponsorship: {},
			engine_supplier: {},
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: []
		})

		document.getElementById('finance-sponsor-replace-btn').click()
		expect(onReplace).toHaveBeenCalledWith('Windale')
	})

	it('keeps title sponsor replace disabled when a pending replacement exists', () => {
		financeView.render({
			balance: 0,
			summary: {},
			sponsor: { name: 'Windale', contract_length: 1, pending_replacement: true, annual_value: 1, installment: 0, paid_so_far: 0, remaining: 1 },
			other_sponsorship: {},
			engine_supplier: {},
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: []
		})

		expect(document.getElementById('finance-sponsor-replace-btn').disabled).toBe(true)
	})
})
