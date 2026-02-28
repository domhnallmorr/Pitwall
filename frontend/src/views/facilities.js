/**
 * Facilities View
 * Displays the player's team factory/facilities rating.
 */

export default class FacilitiesView {
	constructor() {
		this.container = document.getElementById('facilities-container');
		this.modal = document.getElementById('facilities-upgrade-modal');
		this.pointsInput = document.getElementById('facilities-upgrade-points');
		this.pointsValue = document.getElementById('facilities-upgrade-points-value');
		this.yearsSelect = document.getElementById('facilities-upgrade-years');
		this.previewBox = document.getElementById('facilities-upgrade-preview');
		this.cancelBtn = document.getElementById('facilities-upgrade-cancel-btn');
		this.confirmBtn = document.getElementById('facilities-upgrade-confirm-btn');
		this.onPreviewRequest = null;
		this.onStartUpgrade = null;
		this.lastPreview = null;
		this.bindModal();
	}

	setPreviewHandler(handler) {
		this.onPreviewRequest = handler;
	}

	setStartUpgradeHandler(handler) {
		this.onStartUpgrade = handler;
	}

	bindModal() {
		if (this.cancelBtn) {
			this.cancelBtn.addEventListener('click', () => this.closeUpgradeModal());
		}
		if (this.pointsInput) {
			this.pointsInput.addEventListener('input', () => {
				if (this.pointsValue) this.pointsValue.textContent = this.pointsInput.value;
				this.requestPreview();
			});
		}
		if (this.yearsSelect) {
			this.yearsSelect.addEventListener('change', () => this.requestPreview());
		}
		if (this.confirmBtn) {
			this.confirmBtn.addEventListener('click', () => {
				if (!this.onStartUpgrade || !this.lastPreview) return;
				this.onStartUpgrade(Number(this.pointsInput.value), Number(this.yearsSelect.value));
			});
		}
	}

	openUpgradeModal() {
		if (!this.modal) return;
		this.modal.style.display = 'flex';
		if (this.pointsValue && this.pointsInput) this.pointsValue.textContent = this.pointsInput.value;
		this.requestPreview();
	}

	closeUpgradeModal() {
		if (!this.modal) return;
		this.modal.style.display = 'none';
	}

	requestPreview() {
		if (!this.onPreviewRequest || !this.pointsInput || !this.yearsSelect) return;
		this.onPreviewRequest(Number(this.pointsInput.value), Number(this.yearsSelect.value));
	}

	renderPreview(preview, status = 'success', message = '') {
		if (!this.previewBox || !this.confirmBtn) return;
		if (status !== 'success') {
			this.previewBox.textContent = message || 'Unable to preview upgrade.';
			this.confirmBtn.disabled = true;
			this.lastPreview = null;
			return;
		}
		this.lastPreview = preview;
		const noEffectiveChange = (preview.effective_points || 0) <= 0;
		this.confirmBtn.disabled = noEffectiveChange;
		this.previewBox.innerHTML = `
			<div>Current: <strong>${preview.current_facilities}</strong> -> Projected: <strong>${preview.projected_facilities}</strong></div>
			<div>Effective upgrade: <strong>+${preview.effective_points}</strong></div>
			<div>Total cost: <strong>$${Number(preview.total_cost || 0).toLocaleString()}</strong></div>
			<div>Repayment: <strong>${preview.total_races}</strong> races @ <strong>$${Number(preview.per_race_payment || 0).toLocaleString()}</strong> per race</div>
		`;
	}

	getRating(value) {
		const numeric = Number(value);
		const clamped = Number.isFinite(numeric) ? Math.max(0, Math.min(100, numeric)) : 0;
		return Math.max(1, Math.ceil(clamped / 20));
	}

	renderRatingBlocks(value) {
		const rating = this.getRating(value);
		let blocks = '';
		for (let i = 1; i <= 5; i += 1) {
			const stateClass = i <= rating ? 'is-filled' : '';
			blocks += `<span class="facilities-rating-block ${stateClass}" aria-hidden="true"></span>`;
		}
		return `<span class="facilities-rating-widget" role="img" aria-label="Facilities rating ${rating} out of 5">${blocks}</span>`;
	}

	render(data) {
		this.container.innerHTML = '';

		const rating = data.facilities || 0;
		const teamName = data.team_name || 'Unknown';

		// Determine tier label and color
		let tier, tierColor;
		if (rating >= 80) {
			tier = 'World Class';
			tierColor = '#22c55e';
		} else if (rating >= 60) {
			tier = 'Competitive';
			tierColor = '#3b82f6';
		} else if (rating >= 40) {
			tier = 'Midfield';
			tierColor = '#f59e0b';
		} else {
			tier = 'Underdeveloped';
			tierColor = '#ef4444';
		}

		this.container.innerHTML = `
			<div class="facilities-card">
				<div class="facilities-header">
					<h3 class="facilities-team-name">${teamName} Factory</h3>
					<span class="facilities-tier" style="color: ${tierColor}">${tier}</span>
				</div>
				<div class="facilities-rating-display">
					<span class="facilities-rating-number" style="color: ${tierColor}">${rating}</span>
					<span class="facilities-rating-max">/ 100</span>
				</div>
				<div class="facilities-bar-bg">
					<div class="facilities-bar-fill" style="width: ${rating}%; background: ${tierColor}"></div>
				</div>
				<div class="facilities-upgrade-actions">
					<button id="facilities-upgrade-open-btn" class="facilities-upgrade-btn" ${data?.upgrade_financing?.active ? 'disabled' : ''}>
						Upgrade
					</button>
					<div class="facilities-upgrade-status">
						${data?.upgrade_financing?.active
							? `Upgrade financing active: $${Number(data.upgrade_financing.remaining || 0).toLocaleString()} remaining (${data.upgrade_financing.races_paid}/${data.upgrade_financing.total_races} races paid)`
							: 'No active facilities financing'}
					</div>
				</div>
			</div>
			<table class="data-table facilities-table">
				<thead>
					<tr>
						<th>Pos</th>
						<th>Team</th>
						<th>Country</th>
						<th>Facilities Rating</th>
					</tr>
				</thead>
				<tbody id="facilities-table-body"></tbody>
			</table>
		`;

		const tbody = this.container.querySelector('#facilities-table-body');
		const teams = (data?.teams || []).slice().sort((a, b) => (b.facilities ?? 0) - (a.facilities ?? 0));
		teams.forEach((team, index) => {
			const tr = document.createElement('tr');
			tr.innerHTML = `
				<td>${index + 1}</td>
				<td>${team.name}</td>
				<td>${team.country || '-'}</td>
				<td>${this.renderRatingBlocks(team.facilities)}</td>
			`;
			tbody.appendChild(tr);
		});

		const openBtn = this.container.querySelector('#facilities-upgrade-open-btn');
		if (openBtn) {
			openBtn.addEventListener('click', () => this.openUpgradeModal());
		}
	}
}
