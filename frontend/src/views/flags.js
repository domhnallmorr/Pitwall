export function toFlagSlug(country) {
	return String(country || '')
		.trim()
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-+|-+$/g, '');
}

export function renderFlagLabel(country, label) {
	const safeCountry = country || 'Unknown';
	const text = label || safeCountry;
	const flagSlug = toFlagSlug(safeCountry);
	const primarySrc = `assets/flags/${encodeURIComponent(safeCountry)}.png`;
	const fallbackSrc = `assets/flags/${flagSlug}.png`;

	return `
		<span class="flag-label">
			<img class="app-flag" src="${primarySrc}" alt="${safeCountry} flag" onerror="if(!this.dataset.fallback){this.dataset.fallback='1';this.src='${fallbackSrc}';}else{this.style.display='none';}">
			<span>${text}</span>
		</span>
	`;
}
