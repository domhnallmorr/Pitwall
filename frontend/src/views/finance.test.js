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
					<div id="finance-overview-income"></div>
					<div id="finance-overview-expenditure"></div>
					<div id="finance-overview-net"></div>
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
				<div id="finance-title-sponsor-negotiation-modal" style="display:none;">
					<button id="finance-title-sponsor-negotiation-close-btn"></button>
					<div id="finance-title-sponsor-negotiation-sponsors"></div>
					<div id="finance-title-sponsor-negotiation-detail"></div>
				</div>
				<div id="finance-engine-negotiation-modal" style="display:none;">
					<button id="finance-engine-negotiation-close-btn"></button>
					<div id="finance-engine-negotiation-suppliers"></div>
					<div id="finance-engine-negotiation-detail"></div>
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
				prize_money_total: 100,
				driver_wage_expense_total: 220000,
				pay_driver_income_total: 0,
				engine_supplier_income_total: 0,
				management_salary_total: 5160000,
				transport_total: 400,
				crash_damage_total: 25000,
				maintenance_total: 12000,
				spares_total: 52500,
				testing_total: 120,
				design_staff_total: 200,
				engineering_staff_total: 180,
				mechanics_staff_total: 160,
				workforce_total: 700,
				commercial_staff_total: 500,
				hospitality_total: 100000,
				factory_overhead_total: 400000,
				engine_supplier_total: 281250,
				engine_supplier_expense_total: 281250,
				tyre_supplier_total: 0,
				fuel_income_total: 0,
				fuel_expense_total: 75000,
				fuel_supplier_total: -75000,
				facilities_total: 0,
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
				direction: 'expense',
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
		expect(document.getElementById('finance-prize-outlook').textContent).toContain('Test prize outlook')
		expect(document.getElementById('finance-prize-money-total').textContent).toBe('$100')
		expect(document.getElementById('finance-driver-wages-total').textContent).toBe('$220,000')
		expect(document.getElementById('finance-management-salary-total').textContent).toBe('$5,160,000')
		expect(document.getElementById('finance-design-staff-total').textContent).toBe('$200')
		expect(document.getElementById('finance-engineering-staff-total').textContent).toBe('$180')
		expect(document.getElementById('finance-mechanics-staff-total').textContent).toBe('$160')
		expect(document.getElementById('finance-commercial-staff-total').textContent).toBe('$500')
		expect(document.getElementById('finance-hospitality-total').textContent).toBe('$100,000')
		expect(document.getElementById('finance-engine-income-total').textContent).toBe('$0')
		expect(document.getElementById('finance-crash-damage-total').textContent).toBe('$25,000')
		expect(document.getElementById('finance-spares-total').textContent).toBe('$52,500')
		expect(document.getElementById('finance-income-total').textContent).toBe('$5,000')
		expect(document.getElementById('finance-fuel-expense-total').textContent).toBe('$75,000')
		expect(document.getElementById('finance-testing-total').textContent).toBe('$120')
		expect(document.getElementById('finance-factory-overhead-total').textContent).toBe('$400,000')
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
				prize_money_total: 0,
				driver_wage_expense_total: 0,
				pay_driver_income_total: 0,
				engine_supplier_income_total: 0,
				management_salary_total: 0,
				transport_total: 0,
				crash_damage_total: 0,
				maintenance_total: 0,
				spares_total: 0,
				testing_total: 0,
				design_staff_total: 0,
				engineering_staff_total: 0,
				mechanics_staff_total: 0,
				workforce_total: 0,
				commercial_staff_total: 0,
				hospitality_total: 0,
				factory_overhead_total: 0,
				engine_supplier_total: 0,
				engine_supplier_expense_total: 0,
				tyre_supplier_total: 0,
				fuel_income_total: 10,
				fuel_expense_total: 0,
				fuel_supplier_total: 10,
				facilities_total: 0,
				sponsorship_total: 0,
			},
			sponsor: { name: null, annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			other_sponsorship: { annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			engine_supplier: { name: null, deal: '-', annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0, direction: 'expense' },
			tyre_supplier: { name: null, deal: '-', annual_value: 0, installment: 0, paid_so_far: 0, remaining: 0 },
			fuel_supplier: { name: null, deal: '-', annual_value: -1000, installment: 50, paid_so_far: 0, remaining: 950, direction: 'income' },
			track_profit_loss: [],
			transactions: [],
		})

		expect(document.getElementById('finance-balance-value').textContent).toBe('-$100')
		expect(document.getElementById('finance-fuel-income-total').textContent).toBe('$10')
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

	it('renders engine supplier works income with positive signs', () => {
		financeView.render({
			overview: {},
			summary: {
				income_total: 750000,
				expense_total: 0,
				net_profit_loss: 750000,
				prize_money_total: 0,
				driver_wage_expense_total: 0,
				pay_driver_income_total: 0,
				engine_supplier_income_total: 750000,
				management_salary_total: 0,
				transport_total: 0,
				crash_damage_total: 0,
				maintenance_total: 0,
				spares_total: 0,
				testing_total: 0,
				design_staff_total: 0,
				engineering_staff_total: 0,
				mechanics_staff_total: 0,
				workforce_total: 0,
				commercial_staff_total: 0,
				hospitality_total: 0,
				factory_overhead_total: 0,
				engine_supplier_total: 750000,
				engine_supplier_expense_total: 0,
				tyre_supplier_total: 0,
				fuel_income_total: 0,
				fuel_expense_total: 0,
				fuel_supplier_total: 0,
				facilities_total: 0,
				sponsorship_total: 0,
			},
			sponsor: {},
			other_sponsorship: {},
			engine_supplier: {
				name: 'Ferano',
				deal: 'works',
				annual_value: -12000000,
				installment: 750000,
				paid_so_far: 750000,
				remaining: 11250000,
				contract_length: 1,
				direction: 'income',
			},
			tyre_supplier: {},
			fuel_supplier: {},
			track_profit_loss: [],
			transactions: [],
		})

		expect(document.getElementById('finance-engine-income-total').textContent).toBe('$750,000')
		expect(document.getElementById('finance-engine-supplier-annual').textContent).toBe('+$12,000,000')
		expect(document.getElementById('finance-engine-supplier-installment').textContent).toBe('+$750,000')
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

	it('renders and drives the title sponsor negotiation modal', () => {
		const onStart = vi.fn()
		const onUpdateStaff = vi.fn()
		const onSign = vi.fn()
		const onHospitality = vi.fn()
		financeView.setStartTitleSponsorNegotiationHandler(onStart)
		financeView.setUpdateTitleSponsorNegotiationStaffHandler(onUpdateStaff)
		financeView.setSignTitleSponsorNegotiatedDealHandler(onSign)
		financeView.setBookTitleSponsorHospitalityHandler(onHospitality)

		financeView.showTitleSponsorNegotiationModal({
			sponsors: [{ id: 7, name: 'Fastlane', wealth: 74, targetable: true }],
			commercial_manager: { name: 'Helena Schwarz', skill: 84 },
			commercial_staff_total: 20,
			hospitality: { available: true, booked: false, cost: 100000, progress_bonus: 1.0, event_name: 'Albert Park', event_week: 10 },
			active_negotiation: {
				sponsor_name: 'Fastlane',
				progress_boxes: 3,
				total_boxes: 5,
				annual_value: 12000000,
				contract_length: 2,
				assigned_staff: 12,
				ready_to_sign: true,
			},
		})

		expect(document.getElementById('finance-title-sponsor-negotiation-modal').style.display).toBe('flex')
		document.querySelector('[data-title-sponsor-id="7"]').click()
		expect(onStart).toHaveBeenCalledWith(7)

		const input = document.getElementById('finance-title-sponsor-negotiation-staff')
		input.value = '15'
		input.dispatchEvent(new window.Event('change', { bubbles: true }))
		expect(onUpdateStaff).toHaveBeenCalledWith(15)

		document.getElementById('finance-title-sponsor-negotiation-sign-btn').click()
		expect(onSign).toHaveBeenCalled()

		document.getElementById('finance-title-sponsor-hospitality-btn').click()
		expect(onHospitality).toHaveBeenCalled()

		document.getElementById('finance-title-sponsor-negotiation-close-btn').click()
		expect(document.getElementById('finance-title-sponsor-negotiation-modal').style.display).toBe('none')

		financeView.showTitleSponsorNegotiationModal({})
		const modal = document.getElementById('finance-title-sponsor-negotiation-modal')
		modal.dispatchEvent(new window.MouseEvent('click', { bubbles: true }))
		expect(modal.style.display).toBe('none')
	})

	it('renders and drives the engine negotiation modal', () => {
		const onStart = vi.fn()
		const onUpdateStaff = vi.fn()
		const onSign = vi.fn()
		const onHospitality = vi.fn()
		financeView.setStartEngineNegotiationHandler(onStart)
		financeView.setUpdateEngineNegotiationStaffHandler(onUpdateStaff)
		financeView.setSignEngineNegotiatedDealHandler(onSign)
		financeView.setBookEngineNegotiationHospitalityHandler(onHospitality)

		financeView.showEngineNegotiationModal({
			suppliers: [{ id: 2, name: 'Mechatron', country: 'Germany', power: 88, resources: 84, targetable: true }],
			commercial_manager: { name: 'Helena Schwarz', skill: 84 },
			commercial_staff_total: 20,
			hospitality: { available: true, booked: false, cost: 100000, progress_bonus: 1.0, event_name: 'Interlagos', event_week: 12 },
			active_negotiation: {
				supplier_name: 'Mechatron',
				assigned_staff: 12,
				progress_boxes: 5,
				total_boxes: 8,
				customer_threshold: 3,
				partner_threshold: 5,
				works_threshold: 8,
				contract_length: 2,
				available_tiers: ['customer', 'partner', 'works'],
				unlocked_tiers: ['customer', 'partner'],
				annual_values: {
					customer: -10000000,
					partner: -12000000,
					works: -15000000,
				},
			},
		})

		expect(document.getElementById('finance-engine-negotiation-modal').style.display).toBe('flex')
		document.querySelector('[data-engine-supplier-id="2"]').click()
		expect(onStart).toHaveBeenCalledWith(2)

		const input = document.getElementById('finance-engine-negotiation-staff')
		input.value = '18'
		input.dispatchEvent(new window.Event('change', { bubbles: true }))
		expect(onUpdateStaff).toHaveBeenCalledWith(18)

		document.querySelector('[data-engine-tier="customer"]').click()
		expect(onSign).toHaveBeenCalledWith('customer')

		document.getElementById('finance-engine-hospitality-btn').click()
		expect(onHospitality).toHaveBeenCalled()

		document.getElementById('finance-engine-negotiation-close-btn').click()
		expect(document.getElementById('finance-engine-negotiation-modal').style.display).toBe('none')

		financeView.showEngineNegotiationModal({})
		const modal = document.getElementById('finance-engine-negotiation-modal')
		modal.dispatchEvent(new window.MouseEvent('click', { bubbles: true }))
		expect(modal.style.display).toBe('none')
	})
})
