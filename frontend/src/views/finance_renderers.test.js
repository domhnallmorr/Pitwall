import { describe, expect, it } from 'vitest'
import {
	formatMoney,
	renderEngineNegotiationDetail,
	renderEngineNegotiationSupplierList,
	renderNegotiationBlockedState,
	renderNegotiationIdleState,
	renderTitleSponsorNegotiationDetail,
	renderTitleSponsorNegotiationSupplierList,
	renderTrackProfitLossHtml,
	renderTransactionsHtml,
} from './finance_renderers.js'

describe('finance_renderers', () => {
	it('formats money values with optional signed output', () => {
		expect(formatMoney(1250000)).toBe('$1,250,000')
		expect(formatMoney(-1250000)).toBe('-$1,250,000')
		expect(formatMoney(1250000, { signed: true })).toBe('+$1,250,000')
		expect(formatMoney(-1250000, { signed: true })).toBe('-$1,250,000')
	})

	it('renders track profit/loss rows and empty state', () => {
		expect(renderTrackProfitLossHtml()).toContain('No track-linked finance yet')

		const html = renderTrackProfitLossHtml([
			{ track: 'Albert Park', type: 'Grand Prix', country: 'Australia', income: 5000, expense: 400, net: 4600 },
			{ track: 'Imola', type: 'Grand Prix', country: 'Italy', income: 0, expense: 500, net: -500 },
		])

		expect(html).toContain('Albert Park')
		expect(html).toContain('Grand Prix')
		expect(html).toContain('Australia')
		expect(html).toContain('+$4,600')
		expect(html).toContain('-$500')
		expect(html).toContain('finance-amount-positive')
		expect(html).toContain('finance-amount-negative')
	})

	it('renders transactions in reverse chronological display order', () => {
		expect(renderTransactionsHtml()).toContain('No transactions yet')

		const html = renderTransactionsHtml([
			{ week: 3, year: 1998, amount: -400, category: 'transport', description: 'Transport to Melbourne' },
			{ week: 4, year: 1998, amount: 1200, category: 'prize_money', description: 'Points payout' },
		])

		expect(html.indexOf('Week 4, 1998')).toBeLessThan(html.indexOf('Week 3, 1998'))
		expect(html).toContain('finance-category-transport')
		expect(html).toContain('+$1,200')
		expect(html).toContain('-$400')
		expect(html).toContain('Prize Money')
	})

	it('renders supplier lists with disabled buttons where needed', () => {
		expect(renderTitleSponsorNegotiationSupplierList()).toContain('No sponsors available')
		expect(renderEngineNegotiationSupplierList()).toContain('No suppliers available')

		const sponsorHtml = renderTitleSponsorNegotiationSupplierList([
			{ id: 1, name: 'Windale', wealth: 78, targetable: true },
			{ id: 2, name: 'Novastar', wealth: 50, targetable: false },
		])
		expect(sponsorHtml).toContain('Windale')
		expect(sponsorHtml).toContain('Wealth 78')
		expect(sponsorHtml).toContain('data-title-sponsor-id="2" disabled')

		const engineHtml = renderEngineNegotiationSupplierList([
			{ id: 1, name: 'Mechatron', country: 'Germany', power: 88, resources: 82, targetable: true },
			{ id: 2, name: 'Torrix', country: 'France', power: 70, resources: 65, targetable: false },
		])
		expect(engineHtml).toContain('Mechatron')
		expect(engineHtml).toContain('Germany')
		expect(engineHtml).toContain('Power 88')
		expect(engineHtml).toContain('Resources 82')
		expect(engineHtml).toContain('data-engine-supplier-id="2" disabled')
	})

	it('renders shared blocked and idle negotiation states', () => {
		const blockedHtml = renderNegotiationBlockedState('Contract too long.')
		expect(blockedHtml).toContain('Negotiations Unavailable')
		expect(blockedHtml).toContain('Contract too long.')

		const idleHtml = renderNegotiationIdleState({
			intro: 'Select a supplier.',
			commercialManager: { name: 'Helena Schwarz', skill: 84 },
			commercialStaffTotal: 49,
		})
		expect(idleHtml).toContain('No Active Negotiation')
		expect(idleHtml).toContain('Select a supplier.')
		expect(idleHtml).toContain('Helena Schwarz')
		expect(idleHtml).toContain('Skill 84')
		expect(idleHtml).toContain('49')
	})

	it('renders title sponsor negotiation detail states', () => {
		expect(renderTitleSponsorNegotiationDetail({ blocked_reason: 'Already have a pending deal.' }))
			.toContain('Already have a pending deal.')

		expect(renderTitleSponsorNegotiationDetail({
			commercial_manager: { name: 'Helena Schwarz', skill: 84 },
			commercial_staff_total: 49,
		})).toContain('Select a sponsor on the left')

		const activeHtml = renderTitleSponsorNegotiationDetail({
			commercial_staff_total: 49,
			hospitality: { available: true, booked: false, cost: 100000, progress_bonus: 1.0, event_name: 'Albert Park', event_week: 10 },
			active_negotiation: {
				sponsor_name: 'Windale',
				total_boxes: 6,
				progress_boxes: 4,
				annual_value: 32500000,
				contract_length: 2,
				assigned_staff: 18,
				ready_to_sign: true,
			},
		})

		expect(activeHtml).toContain('Windale')
		expect(activeHtml).toContain('Progress: 4/6 boxes')
		expect(activeHtml).toContain('value="18"')
		expect(activeHtml).toContain('Invite To Next Race')
		expect(activeHtml).toContain('Albert Park (Week 10)')
		expect(activeHtml).toContain('$100,000')
		expect(activeHtml).toContain('Sign Deal ($32,500,000)')
		expect(activeHtml).not.toContain('finance-title-sponsor-negotiation-sign-btn" class="btn-primary" disabled')
		expect((activeHtml.match(/finance-engine-progress-box filled/g) || [])).toHaveLength(4)
	})

	it('renders engine negotiation detail states with tier unlocks', () => {
		expect(renderEngineNegotiationDetail({ blocked_reason: 'Current deal is too long.' }))
			.toContain('Current deal is too long.')

		expect(renderEngineNegotiationDetail({
			commercial_manager: { name: 'Helena Schwarz', skill: 84 },
			commercial_staff_total: 49,
		})).toContain('Select a supplier on the left')

		const activeHtml = renderEngineNegotiationDetail({
			commercial_staff_total: 49,
			hospitality: { available: false, booked: true, cost: 100000, progress_bonus: 1.0, reason: 'Hospitality is already booked for Albert Park (Week 10).', event_name: 'Albert Park', event_week: 10 },
			active_negotiation: {
				supplier_name: 'Mechatron',
				total_boxes: 8,
				progress_boxes: 5,
				customer_threshold: 2,
				partner_threshold: 5,
				works_threshold: 8,
				contract_length: 2,
				assigned_staff: 20,
				available_tiers: ['customer', 'partner', 'works'],
				unlocked_tiers: ['customer', 'partner'],
				annual_values: {
					customer: 4500000,
					partner: 1200000,
					works: -3000000,
				},
			},
		})

		expect(activeHtml).toContain('Mechatron')
		expect(activeHtml).toContain('Progress: 5/8 boxes')
		expect(activeHtml).toContain('Unlocked')
		expect(activeHtml).toContain('Customer, Partner')
		expect(activeHtml).toContain('data-engine-tier="customer"')
		expect(activeHtml).toContain('data-engine-tier="partner"')
		expect(activeHtml).toContain('data-engine-tier="works" disabled')
		expect(activeHtml).toContain('Sign Customer (-$4,500,000)')
		expect(activeHtml).toContain('Sign Works (+$3,000,000)')
		expect(activeHtml).toContain('Hospitality booked for Albert Park (Week 10)')
		expect(activeHtml).toContain('finance-engine-hospitality-btn')
		expect(activeHtml).toContain('value="20"')
		expect((activeHtml.match(/finance-engine-progress-box filled/g) || [])).toHaveLength(5)
	})
})
