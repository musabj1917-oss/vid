require('dotenv').config();
const cron = require('node-cron');
const { runPipeline } = require('./runner');

console.log(`[${new Date().toISOString()}] 🕒 Video Creation Scheduler Initialized`);
console.log(`📅 Schedules active:`);
console.log(`   - 12:30 PM daily ('30 12 * * *')`);
console.log(`   - 7:30 PM daily  ('30 19 * * *')`);

// Schedule 1: 12:30 PM daily
cron.schedule('30 12 * * *', () => {
  console.log(`\n[${new Date().toISOString()}] ⏰ [12:30 PM] Triggering scheduled video pipeline...`);
  runPipeline();
});

// Schedule 2: 7:30 PM daily
cron.schedule('30 19 * * *', () => {
  console.log(`\n[${new Date().toISOString()}] ⏰ [7:30 PM] Triggering scheduled video pipeline...`);
  runPipeline();
});
