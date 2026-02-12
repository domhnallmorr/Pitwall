import { app } from 'electron';
console.log('App is:', app);
console.log('Process versions:', process.versions);
if (app) app.quit();
