const electron = require('electron');
console.log('Type of electron:', typeof electron);
console.log('Value of electron:', electron);
try {
	console.log('Resolved path:', require.resolve('electron'));
} catch (e) {
	console.log('Could not resolve electron path');
}
if (typeof electron === 'object') {
	console.log('Keys:', Object.keys(electron));
}
console.log('Process versions:', process.versions);
