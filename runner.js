const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const TOPIC_POOL = [
  "Why your business website is losing you high-paying clients and how to fix it in 3 steps",
  "The 3 silent conversion killers on small business landing pages",
  "Why relying solely on social media pages instead of an official website hurts your brand trust",
  "How page load speed under 2 seconds directly doubles your customer inquiries",
  "How an automated booking and menu system frees up 15 hours a week for local business owners"
];

function getNextTopic() {
  const dir = path.join(__dirname, '.pipeline');
  const file = path.join(dir, 'topic_index.txt');
  let index = 0;
  if (fs.existsSync(file)) {
    index = parseInt(fs.readFileSync(file, 'utf8'), 10) || 0;
  }
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(file, String(index + 1));
  return TOPIC_POOL[index % TOPIC_POOL.length];
}

function runPipeline() {
  const topic = getNextTopic();
  console.log(`\n[${new Date().toISOString()}] 🚀 Launching Pipeline: "${topic}"`);
  const prompt = `@video-pipeline Run fully autonomously for topic: "${topic}". Review and upload automatically without interactive confirmation.`;
  const child = spawn('agy', ['-p', prompt, '--dangerously-skip-permissions'], { stdio: 'inherit' });

  child.on('close', (code) => {
    if (code === 0) console.log(`[${new Date().toISOString()}] ✅ Completed successfully.`);
    else console.error(`[${new Date().toISOString()}] ❌ Failed with exit code ${code}.`);
  });
}

if (require.main === module) runPipeline();
module.exports = { runPipeline, getNextTopic };
