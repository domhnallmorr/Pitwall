/**
 * Email View Module
 * Handles rendering the inbox list and email detail pane.
 */

import API from '../api.js';

export default class EmailView {
	constructor() {
		this.emailList = document.getElementById('email-list');
		this.emailDetail = document.getElementById('email-detail');
		this.emails = [];
		this.selectedId = null;
	}

	render(data) {
		this.emails = data.emails;
		this.updateUnreadBadge(data.unread_count);
		this.renderList();

		// If we had a selected email, keep it selected
		if (this.selectedId) {
			this.showDetail(this.selectedId);
		} else {
			this.emailDetail.innerHTML = '<div class="email-detail-placeholder">Select an email to read</div>';
		}
	}

	renderList() {
		this.emailList.innerHTML = '';

		this.emails.forEach(email => {
			const item = document.createElement('div');
			item.className = `email-item${email.read ? '' : ' unread'}${email.id === this.selectedId ? ' selected' : ''}`;
			item.dataset.emailId = email.id;

			item.innerHTML = `
				<div class="email-item-sender">${email.sender}</div>
				<div class="email-item-subject">${email.subject}</div>
				<div class="email-item-meta">Week ${email.week}, ${email.year}</div>
			`;

			item.addEventListener('click', () => {
				this.selectEmail(email.id);
			});

			this.emailList.appendChild(item);
		});
	}

	selectEmail(emailId) {
		this.selectedId = emailId;
		const email = this.emails.find(e => e.id === emailId);

		if (!email) return;

		// Mark as read
		if (!email.read) {
			email.read = true;
			API.readEmail(emailId);
		}

		this.showDetail(emailId);
		this.renderList(); // Re-render to update unread styling
	}

	showDetail(emailId) {
		const email = this.emails.find(e => e.id === emailId);
		if (!email) return;

		// Format body with line breaks
		const formattedBody = email.body.replace(/\n/g, '<br>');

		this.emailDetail.innerHTML = `
			<div class="email-detail-header">
				<h3 class="email-detail-subject">${email.subject}</h3>
				<div class="email-detail-meta">
					<span class="email-detail-sender">From: ${email.sender}</span>
					<span class="email-detail-date">Week ${email.week}, ${email.year}</span>
				</div>
			</div>
			<div class="email-detail-body">${formattedBody}</div>
		`;
	}

	updateUnreadBadge(count) {
		const badge = document.getElementById('email-unread-badge');
		// Also update sidebar badge
		const sidebarBadge = document.getElementById('email-sidebar-badge');

		if (count > 0) {
			if (badge) {
				badge.textContent = count;
				badge.style.display = 'inline';
			}
			if (sidebarBadge) {
				sidebarBadge.textContent = count;
				sidebarBadge.style.display = 'inline';
			}
		} else {
			if (badge) badge.style.display = 'none';
			if (sidebarBadge) sidebarBadge.style.display = 'none';
		}
	}
}
