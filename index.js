require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { generateCoverLetter } = require('./openai-helper');
const { runPuppeteerApply } = require('./puppeteer-runner');
const { logToSheet } = require('./google-sheets');

async function loadAutomations() {
  const raw = fs.readFileSync(path.join(__dirname,'automations.json'),'utf8');
  return JSON.parse(raw);
}

async function findJobsForAutomation(automation) {
  // This is a placeholder: in production use site APIs or scrapers per-site.
  // Example returns an array of job objects: {title, company, url, description}
  // For demo, return a fake job:
  return [{
    title: "Product Designer",
    company: "Acme Startups",
    url: "https://example.com/jobs/123",
    description: "We need a Product Designer experienced in Figma and prototyping..."
  }];
}

async function processAutomation(automation) {
  console.log('Processing:', automation.title);
  const jobs = await findJobsForAutomation(automation);
  for (const job of jobs) {
    try {
      // 1. Generate cover letter tailored to JD + your profile
      const cover = await generateCoverLetter({
        jobDescription: job.description,
        candidateProfile: {
          name: process.env.USER_NAME,
          highlights: ["Figma", "prototyping", "user research"]
        },
        tone: "professional, confident"
      });

      // 2. Optionally adjust resume (not implemented here - could call OpenAI to rewrite bullets)
      // 3. Launch Puppeteer to autofill and apply (may require login)
      const result = await runPuppeteerApply({
        jobUrl: job.url,
        resumePath: process.env.RESUME_PATH,
        coverLetterText: cover,
        metadata: { automationId: automation.id, jobTitle: job.title }
      });

      // 4. Log result
      await logToSheet({
        automationId: automation.id,
        jobTitle: job.title,
        company: job.company,
        url: job.url,
        status: result.success ? 'applied' : 'failed',
        notes: result.message
      });

      console.log('Result:', job.title, result.success);
      // Respect rate limits: wait between applications
      await new Promise(r => setTimeout(r, 5000));
    } catch (err) {
      console.error('Error processing job', job.url, err);
    }
  }
}

(async () => {
  const automations = await loadAutomations();
  for (const a of automations) {
    if (a.type !== 'job-apply') continue;
    await processAutomation(a);
  }
  console.log('All automations processed.');
})();
