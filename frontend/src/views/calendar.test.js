import { describe, it, expect, beforeEach } from 'vitest'
import CalendarView from './calendar.js'
import { JSDOM } from 'jsdom'

describe('CalendarView', () => {
	let dom
	let calendarView

	beforeEach(() => {
		// Setup DOM
		dom = new JSDOM(`
            <div id="calendar-view">
                <select id="calendar-filter">
                    <option value="all">All</option>
                    <option value="Grand Prix">GP</option>
                    <option value="Test">Test</option>
                </select>
                <table>
                    <tbody id="calendar-table-body"></tbody>
                </table>
            </div>
        `)
		global.document = dom.window.document
		global.window = dom.window

		calendarView = new CalendarView()
	})

	const mockData = [
		{ round: '1', week: 5, type: 'Grand Prix', track: 'Albert Park', country: 'Australia', winner: '' },
		{ round: '-', week: 2, type: 'Test', track: 'Test Track', country: 'Spain', winner: '' },
		{ round: '2', week: 10, type: 'Grand Prix', track: 'Monaco', country: 'Monaco', winner: '' }
	]

	it('renders all events by default', () => {
		calendarView.render(mockData)
		const rows = document.querySelectorAll('tr')
		expect(rows.length).toBe(3)
		expect(rows[0].innerHTML).toContain('Albert Park')
	})

	it('renders message if no data', () => {
		calendarView.render([])
		const rows = document.querySelectorAll('tr')
		expect(rows.length).toBe(1)
		expect(rows[0].innerHTML).toContain('No events found')
	})

	it('filters correctly for Grand Prix', () => {
		calendarView.render(mockData)

		// Simulate filter change
		calendarView.filterSelect.value = 'Grand Prix'
		calendarView.applyFilter() // Manually trigger since event listener mock is tricky without full interaction

		const rows = document.querySelectorAll('tr')
		expect(rows.length).toBe(2)
		expect(rows[0].innerHTML).toContain('Albert Park')
		expect(rows[1].innerHTML).toContain('Monaco')
	})

	it('filters correctly for Tests', () => {
		calendarView.render(mockData)

		calendarView.filterSelect.value = 'Test'
		calendarView.applyFilter()

		const rows = document.querySelectorAll('tr')
		expect(rows.length).toBe(1)
		expect(rows[0].innerHTML).toContain('Test Track')
	})
})
