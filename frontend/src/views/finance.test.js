import { describe, it, expect, beforeEach, vi } from 'vitest'
import { JSDOM } from 'jsdom'
import FinanceView from './finance.js'
import { renderLayoutPartials } from '../layout/partials.js'

describe('FinanceView', () => {
	let financeView

	beforeEach(() => {
		const dom = new JSDOM(`
			<div id="finance-view">
				<button class="finance-tab-btn active" data-type="overview"></button>
				<button class="finance-tab-btn" data-type="commercial"></button>
				<button class="finance-tab-btn" data-type="suppliers"></button>
				<button class="finance-tab-btn" data-type="ledger"></button>
				<div id="finance-content-overview">
					<div id="finance-summary"></div>
					<div id="finance-overview-breakdown"></div>
					<div id="finance-overview-planning"></div>
					<div id="finance-prize-progress"></div>
					<ul id="finance-contract-alerts"></ul>
				</div>
				<div id="finance-content-commercial" style="display:none;">
					<div id="finance-commercial-sections"></div>
				</div>
				<div id="finance-content-suppliers" style="display:none;">
					<div id="finance-supplier-sections"></div>
				</div>
				<div id="finance-content-ledger" style="display:none;">
					<table><tbody id="finance-track-pl-body"></tbody></table>
					<table><tbody id="finance-transactions-body"></tbody></table>
				</div>
			</div>
		`)
		global.document = dom.window.document
		global.window = dom.window
		renderLayoutPartials()
		financeView = new FinanceView()
	})

	it('renders overview, commercial cards, supplier cards, and ledger rows', () => {
		financeView.render({
			balance: 1000,
			prize_money_entitlement: 3000,
			prize_money_paid: 1000,
			prize_money_remaining: 2000,
			prize_money_races_paid: 1,
			prize_money_total_races: 10,
			overview: {
				projected_end_balance: 8500,
				next_race_income: 2600000,
				next_race_outgoings: 400000,
				next_race_net: 2200000,
				prize_outlook: 'Test prize outlook',
				facilities_status: 'No active facilities financing.',
				contract_alerts: ['Title sponsor deal expires after this season.'],
			},
			summary: {
				income_total: 5000,
				expense_total: 1200,
				net_profit_loss: 3800,
				transport_total: 400,
				testing_total: 120,
				workforce_total: 700,
				engine_supplier_total: 281250,
				tyre_supplier_total: 0,
				fuel_supplier_total: -75000,
				sponsorship_total: 900,
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
				contract_length: 1,
			},
			tyre_supplier: {
				name: 'Greatday',
				deal: 'partner',
				annual_value: 0,
				installment: 0,
				paid_so_far: 0,
				remaining: 0,
				contract_length: 1,
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
				{ track: 'Albert Park', type: 'Grand Prix', country: 'Australia', income: 5000, expense: 400, net: 4600 },
			],
			transactions: [
				{ week: 10, year: 1998, amount: -400, category: 'transport', description: 'Transport to Albert Park' },
			],
		})

		expect(document.getElementById('finance-projected-balance').textContent).toBe('$8,500')
		expect(document.getElementById('finance-next-race-net').textContent).toBe('$2,200,000')
		expect(document.getElementById('finance-next-race-income').textContent).toBe('$2,600,000')
		expect(document.getElementById('finance-prize-outlook').textContent).toContain('Test prize outlook')
		expect(document.getElementById('finance-income-total').textContent).toBe('$5,000')
		expect(document.getElementById('finance-fuel-supplier-total').textContent).toBe('-$75,000')
		expect(document.getElementById('finance-testing-total').textContent).toBe('$120')
		expect(document.getElementById('finance-sponsor-name').textContent).toBe('Windale')
		expect(document.getElementById('finance-sponsor-replace-btn').disabled).toBe(false)
		expect(document.getElementById('finance-engine-supplier-name').textContent).toBe('Mechatron')
		expect(document.getElementById('finance-engine-supplier-replace-btn').disabled).toBe(false)
		expect(document.getElementById('finance-tyre-supplier-name').textContent).toBe('Greatday')
		expect(document.getElementById('finance-tyre-supplier-replace-btn').disabled).toBe(false)
		expect(document.getElementById('finance-fuel-supplier-annual').textContent).toBe('-$150,000')
		expect(document.getElementById('finance-contract-alerts').textContent).toContain('Title sponsor deal expires')
		expect(document.querySelectorAll('#finance-track-pl-body tr')).toHaveLength(1)
		expect(document.getElementById('finance-track-pl-body').textContent).toContain('Grand Prix')
		expect(document.querySelectorAll('#finance-transactions-body tr')).toHaveLength(1)
	})

	it('handles tab switching, empty states, and disabled replacement buttons', () => {
		financeView.render({
			balance: -100,
			overview: {
				projected_end_balance: -500,
				next_race_income: 100,
				next_race_outgoings: 90,
				next_race_net: 10,
				prize_outlook: 'All prize money paid.',
				facilities_status: 'No active facilities financing.',
				contract_alerts: [],
			},
			summary: {
				income_total: 0,
				expense_total: 0,
				net_profit_loss: -100,
				transport_total: 0,
				testing_total: 0,
				workforce_total: 0,
				engine_supplier_total: 0,
				tyre_supplier_total: 0,
				fuel_supplier_total: 10,
				sponsorship_total: 0,
			},
			sponsor: { name: null, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			other_sponsorship: { annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			engine_supplier: { name: null, deal: '-', annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			tyre_supplier: { name: null, deal: '-', annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			fuel_supplier: { name: null, deal: '-', annual_value: -1000, installment: 50, paid_so_far: 0, remaining: 950, direction: 'income' },
			track_profit_loss: [],
			transactions: [],
		})

		expect(document.getElementById('finance-balance-value').textContent).toBe('-$100')
		expect(document.getElementById('finance-fuel-supplier-total').textContent).toBe('+$10')
		expect(document.getElementById('finance-fuel-supplier-installment').textContent).toBe('+$50')
		expect(document.getElementById('finance-track-pl-body').textContent).toContain('No track-linked finance yet')
		expect(document.getElementById('finance-transactions-body').textContent).toContain('No transactions yet')
		expect(document.getElementById('finance-sponsor-logo-wrap').innerHTML).toBe('')
		expect(document.getElementById('finance-sponsor-replace-btn').disabled).toBe(true)
		expect(document.getElementById('finance-engine-supplier-replace-btn').disabled).toBe(true)
		expect(document.getElementById('finance-tyre-supplier-replace-btn').disabled).toBe(true)
		expect(document.getElementById('finance-contract-alerts').textContent).toContain('No immediate contract risks')

		const ledgerBtn = document.querySelector('.finance-tab-btn[data-type="ledger"]')
		ledgerBtn.click()
		expect(document.getElementById('finance-content-overview').style.display).toBe('none')
		expect(document.getElementById('finance-content-ledger').style.display).toBe('block')
	})

	it('triggers title sponsor replace handler when enabled', () => {
		const onReplace = vi.fn()
		financeView.setReplaceTitleSponsorHandler(onReplace)
		financeView.render({
			overview: {},
			summary: {},
			sponsor: { name: 'Windale', contract_length: 1, annual_value: 1, installment: 0, paid_so_far: 0, remaining: 1 },
			other_sponsorship: {},
			engine_supplier: {},
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})

		document.getElementById('finance-sponsor-replace-btn').click()
		expect(onReplace).toHaveBeenCalledWith('Windale')
	})

	it('keeps title sponsor replace disabled when a pending replacement exists', () => {
		financeView.render({
			overview: {},
			summary: {},
			sponsor: { name: 'Windale', contract_length: 1, pending_replacement: true, annual_value: 1, installment: 0, paid_so_far: 0, remaining: 1 },
			other_sponsorship: {},
			engine_supplier: {},
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})

		expect(document.getElementById('finance-sponsor-replace-btn').disabled).toBe(true)
	})

	it('triggers tyre supplier replace handler when enabled and disables on pending replacement', () => {
		const onReplace = vi.fn()
		financeView.setReplaceTyreSupplierHandler(onReplace)
		financeView.render({
			overview: {},
			summary: {},
			sponsor: {},
			other_sponsorship: {},
			engine_supplier: {},
			tyre_supplier: { name: 'Greatday', contract_length: 1, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})

		document.getElementById('finance-tyre-supplier-replace-btn').click()
		expect(onReplace).toHaveBeenCalledWith('Greatday')

		financeView.render({
			overview: {},
			summary: {},
			sponsor: {},
			other_sponsorship: {},
			engine_supplier: {},
			tyre_supplier: { name: 'Greatday', contract_length: 1, pending_replacement: true, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})

		expect(document.getElementById('finance-tyre-supplier-replace-btn').disabled).toBe(true)
	})

	it('triggers engine supplier replace handler when enabled and disables for self-built or pending replacement', () => {
		const onReplace = vi.fn()
		financeView.setReplaceEngineSupplierHandler(onReplace)
		financeView.render({
			overview: {},
			summary: {},
			sponsor: {},
			other_sponsorship: {},
			engine_supplier: { name: 'Mechatron', contract_length: 1, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})

		document.getElementById('finance-engine-supplier-replace-btn').click()
		expect(onReplace).toHaveBeenCalledWith('Mechatron')

		financeView.render({
			overview: {},
			summary: {},
			sponsor: {},
			other_sponsorship: {},
			engine_supplier: { name: 'Ferano', contract_length: 0, builds_own_engine: true, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})
		expect(document.getElementById('finance-engine-supplier-replace-btn').disabled).toBe(true)

		financeView.render({
			overview: {},
			summary: {},
			sponsor: {},
			other_sponsorship: {},
			engine_supplier: { name: 'Mechatron', contract_length: 1, pending_replacement: true, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})
		expect(document.getElementById('finance-engine-supplier-replace-btn').disabled).toBe(true)
	})
})
