function updateBalance(balanceEl, amount) {
	const formatted = '$' + Math.abs(amount).toLocaleString();
	balanceEl.textContent = amount < 0 ? '-' + formatted : formatted;
	balanceEl.className = amount < 0 ? 'balance-info balance-negative' : 'balance-info';
}

function formatMoney(amount) {
	const formatted = '$' + Math.abs(Number(amount || 0)).toLocaleString();
	return amount < 0 ? '-' + formatted : formatted;
}

function formatOrdinal(value) {
	if (!value) return '-';
	const mod10 = value % 10;
	const mod100 = value % 100;
	if (mod10 === 1 && mod100 !== 11) return `${value}st`;
	if (mod10 === 2 && mod100 !== 12) return `${value}nd`;
	if (mod10 === 3 && mod100 !== 13) return `${value}rd`;
	return `${value}th`;
}

export function renderHomeView(payload) {
	const homeView = document.getElementById('home-view');
	if (!homeView || !payload) return;

	const top = payload.top_summary || {};
	const nextUp = payload.next_up || {};
	const season = payload.season_snapshot || {};
	const team = payload.team_snapshot || {};
	const finance = payload.finance_snapshot || {};
	const alerts = Array.isArray(payload.alerts) ? payload.alerts : [];
	const recentNews = Array.isArray(payload.recent_news) ? payload.recent_news : [];
	const latestResult = season.latest_result || null;
	const latestResultText = latestResult
		? `${latestResult.event_name || 'Latest race'}: P${latestResult.position || '-'}${latestResult.points !== undefined ? `, ${latestResult.points} pts` : ''}`
		: 'No race result recorded yet';

	homeView.innerHTML = `
		<div class="view-header">
			<h2>Home</h2>
		</div>
		<div class="home-dashboard">
			<section class="home-summary-grid">
				<div class="home-summary-card">
					<span class="home-kicker">Week</span>
					<strong>${top.week_display || '-'}</strong>
				</div>
				<div class="home-summary-card">
					<span class="home-kicker">Balance</span>
					<strong>${formatMoney(top.balance || 0)}</strong>
				</div>
				<div class="home-summary-card">
					<span class="home-kicker">Constructors</span>
					<strong>${formatOrdinal(top.constructors_position)}${top.constructors_points !== undefined ? ` · ${top.constructors_points} pts` : ''}</strong>
				</div>
				<div class="home-summary-card">
					<span class="home-kicker">Next Event</span>
					<strong>${top.next_event_display || 'TBC'}</strong>
				</div>
			</section>
			<div class="home-main-grid">
				<section class="home-panel">
					<h3>Next Up</h3>
					<div class="home-next-up">
						<div>
							<span class="home-kicker">Sidebar Action</span>
							<strong>${nextUp.sidebar_action || 'ADVANCE'}</strong>
						</div>
						<div>
							<span class="home-kicker">Event</span>
							<strong>${nextUp.event_name || 'No active event'}</strong>
						</div>
					</div>
				</section>
				<section class="home-panel">
					<h3>Alerts</h3>
					<ul class="home-list">
						${alerts.length ? alerts.map((alert) => `<li>${alert}</li>`).join('') : '<li>No immediate issues</li>'}
					</ul>
				</section>
				<section class="home-panel">
					<h3>Season Snapshot</h3>
					<div class="home-stat-grid">
						<div><span class="home-kicker">Lead Driver</span><strong>${season.lead_driver_name || '-'}</strong></div>
						<div><span class="home-kicker">Driver Position</span><strong>${formatOrdinal(season.lead_driver_position)}</strong></div>
						<div><span class="home-kicker">Wins</span><strong>${season.wins ?? 0}</strong></div>
						<div><span class="home-kicker">Podiums</span><strong>${season.podiums ?? 0}</strong></div>
					</div>
					<p class="home-note">${latestResultText}</p>
				</section>
				<section class="home-panel">
					<h3>Team Snapshot</h3>
					<div class="home-stat-grid">
						<div><span class="home-kicker">Drivers</span><strong>${(team.drivers || []).join(' / ') || 'VACANT'}</strong></div>
						<div><span class="home-kicker">Team Principal</span><strong>${team.team_principal || 'You'}</strong></div>
						<div><span class="home-kicker">Technical Director</span><strong>${team.technical_director || 'VACANT'}</strong></div>
						<div><span class="home-kicker">Commercial Manager</span><strong>${team.commercial_manager || 'VACANT'}</strong></div>
						<div><span class="home-kicker">Title Sponsor</span><strong>${team.title_sponsor || 'VACANT'}</strong></div>
						<div><span class="home-kicker">Suppliers</span><strong>${team.engine_supplier || 'VACANT'} / ${team.tyre_supplier || 'VACANT'} / ${team.fuel_supplier || 'VACANT'}</strong></div>
					</div>
				</section>
				<section class="home-panel">
					<h3>Finance Snapshot</h3>
					<div class="home-stat-grid">
						<div><span class="home-kicker">Balance</span><strong>${formatMoney(finance.balance || 0)}</strong></div>
						<div><span class="home-kicker">Season Net</span><strong>${formatMoney(finance.season_net || 0)}</strong></div>
						<div><span class="home-kicker">Prize Money</span><strong>${formatMoney(finance.prize_money_total || 0)}</strong></div>
						<div><span class="home-kicker">Sponsorship</span><strong>${formatMoney(finance.sponsorship_total || 0)}</strong></div>
					</div>
				</section>
				<section class="home-panel">
					<h3>Latest News</h3>
					<ul class="home-list home-news-list">
						${recentNews.length ? recentNews.map((item) => `<li><strong>${item.subject}</strong><span>${item.sender} · W${item.week} ${item.year}</span></li>`).join('') : '<li>No recent messages</li>'}
					</ul>
				</section>
			</div>
		</div>
	`;
}

export function handleGameStart({
	data,
	titleScreen,
	dashboard,
	gridView,
	teamNameEl,
	weekEl,
	nextEventEl,
	balanceEl,
	emailView,
	api,
}) {
	titleScreen.style.display = 'none';
	dashboard.style.display = 'flex';
	gridView.setSeasonBase(data.year);

	teamNameEl.textContent = data.team_name;
	weekEl.textContent = data.week_display;
	nextEventEl.textContent = data.next_event_display;
	if (data.balance !== undefined) updateBalance(balanceEl, data.balance);
	if (data.unread_count !== undefined) emailView.updateUnreadBadge(data.unread_count);

	api.getHome();
	api.getStandings();
	api.getGrid(data.year);
	api.getGrid(data.year + 1);
}

export function updateDashboard({ data, weekEl, nextEventEl, balanceEl, gridView, api }) {
	weekEl.textContent = data.new_date_display;
	nextEventEl.textContent = data.next_event_display;
	if (data.balance !== undefined) updateBalance(balanceEl, data.balance);

	const advanceBtn = document.getElementById('advance-btn');
	if (advanceBtn && data.button_text) {
		advanceBtn.textContent = data.button_text;
		if (data.event_active) advanceBtn.classList.add('event-active');
		else advanceBtn.classList.remove('event-active');
	}

	if (data.year && Number(data.year) !== gridView.baseYear) {
		gridView.setSeasonBase(data.year);
		api.getGrid(data.year);
		api.getGrid(data.year + 1);
	}
}

export function showTeamSelect({ titleStartActions, teamSelectScreen, teamSelectButtons, teamOptions, api }) {
	if (titleStartActions) titleStartActions.style.display = 'none';
	if (!teamSelectScreen || !teamSelectButtons) return;
	teamSelectButtons.innerHTML = '';

	teamOptions.forEach((teamName) => {
		const btn = document.createElement('button');
		btn.className = 'team-select-btn';
		btn.textContent = teamName;
		btn.addEventListener('click', () => {
			console.log(`Starting Career as ${teamName}...`);
			api.startCareer(teamName);
		});
		teamSelectButtons.appendChild(btn);
	});

	teamSelectScreen.style.display = 'block';
}

export function refreshVisibleViews({ gridView, driverView, api }) {
	const gridEl = document.getElementById('grid-view');
	if (gridEl && gridEl.style.display !== 'none') api.getGrid(gridView.getActiveYear());

	const staffEl = document.getElementById('staff-view');
	if (staffEl && staffEl.style.display !== 'none') api.getStaff();

	const carEl = document.getElementById('car-view');
	if (carEl && carEl.style.display !== 'none') api.getCar();

	const standingsEl = document.getElementById('standings-view');
	if (standingsEl && standingsEl.style.display !== 'none') api.getStandings();

	const driverEl = document.getElementById('driver-view');
	if (driverEl && driverEl.style.display !== 'none' && driverView?.currentDriverName) {
		api.getDriver(driverView.currentDriverName);
	}

	const financeEl = document.getElementById('finance-view');
	if (financeEl && financeEl.style.display !== 'none') api.getFinance();

	const facilitiesEl = document.getElementById('facilities-view');
	if (facilitiesEl && facilitiesEl.style.display !== 'none') api.getFacilities();

	const homeEl = document.getElementById('home-view');
	if (homeEl && homeEl.style.display !== 'none') api.getHome();
}

export function openDriverProfile(driverName, navigation, api) {
	if (!driverName) return;
	if (navigation) navigation.showView('driver');
	api.getDriver(driverName);
}
