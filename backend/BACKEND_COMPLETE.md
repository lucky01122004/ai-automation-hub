# Complete Backend Setup - Job Application Automation

## ✅ Files Already Created
- package.json
- .env.example

## 📁 Remaining Files - Copy These Into Your Backend Folder

### 1. index.js (Main Server + Runner)
```javascript
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs-extra');
const puppeteer = require('puppeteer');
const { generateCoverLetter } = require('../openai-helper');
const { runLinkedInEasyApply } = require('./linkedin-runner');
const { runGreenhouseApply } = require('./greenhouse-runner');
const { appendToSheet } = require('./google-sheets-helper');

const app = express();
app.use(cors());
app.use(express.json());

const HISTORY_PATH = './history.json';

// Ensure history file exists
if (!fs.existsSync(HISTORY_PATH)) fs.writeFileSync(HISTORY_PATH, '[]', 'utf8');

// API Endpoints
app.get('/history', (req, res) => {
  const data = fs.readJsonSync(HISTORY_PATH);
  res.json(data);
});

app.post('/push-history', (req, res) => {
  const entry = { timestamp: new Date().toISOString(), ...req.body };
  const data = fs.readJsonSync(HISTORY_PATH);
  data.unshift(entry);
  fs.writeJsonSync(HISTORY_PATH, data, { spaces: 2 });
  res.json({ ok: true });
});

// Main job application runner
async function runJobApply() {
  console.log('Starting job application automation...');
  
  // Sample jobs - replace with your job finding logic
  const jobs = [
    {
      title: 'Product Designer',
      company: 'Acme Startups',
      url: 'https://example.com/jobs/123',
      description: 'We need a Product Designer experienced in Figma and prototyping...'
    }
  ];

  for (const job of jobs) {
    try {
      // Generate AI cover letter
      const cover = await generateCoverLetter({
        jobDescription: job.description,
        candidateProfile: {
          name: process.env.USER_NAME,
          highlights: ['Figma', 'prototyping', 'user research']
        },
        tone: 'professional, confident'
      });

      // Choose runner based on job site
      let result;
      if (job.url.includes('linkedin.com')) {
        result = await runLinkedInEasyApply({
          jobUrl: job.url,
          resumePath: process.env.RESUME_PATH,
          coverLetter: cover
        });
      } else if (job.url.includes('greenhouse.io')) {
        result = await runGreenhouseApply({
          jobUrl: job.url,
          resumePath: process.env.RESUME_PATH,
          coverLetter: cover
        });
      } else {
        result = await runGenericApply(job, cover);
      }

      // Log result
      await logHistory({
        automationId: 'auto_' + Date.now(),
        jobTitle: job.title,
        company: job.company,
        url: job.url,
        status: result.success ? 'applied' : 'failed',
        notes: result.message
      });

      console.log(`Result for ${job.title}:`, result.success);
      
      // Rate limiting
      await new Promise(r => setTimeout(r, 5000));
    } catch (err) {
      console.error('Error processing job:', err);
    }
  }
}

async function logHistory(entry) {
  // Save to local JSON
  const data = fs.readJsonSync(HISTORY_PATH);
  data.unshift({ timestamp: new Date().toISOString(), ...entry });
  fs.writeJsonSync(HISTORY_PATH, data, { spaces: 2 });
  console.log('History saved:', entry.jobTitle);

  // Optional: Save to Google Sheets
  if (process.env.GS_SPREADSHEET_ID && process.env.GS_KEYFILE_PATH) {
    try {
      await appendToSheet({
        spreadsheetId: process.env.GS_SPREADSHEET_ID,
        keyFile: process.env.GS_KEYFILE_PATH,
        row: [
          entry.timestamp,
          entry.automationId,
          entry.jobTitle,
          entry.company,
          entry.url,
          entry.status,
          entry.notes || ''
        ]
      });
      console.log('Appended to Google Sheet');
    } catch (e) {
      console.warn('Sheets append failed:', e.message);
    }
  }
}

async function runGenericApply(job, cover) {
  const browser = await puppeteer.launch({
    headless: process.env.HEADLESS !== 'false',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  try {
    await page.goto(job.url, { waitUntil: 'networkidle2', timeout: 60000 });
    console.log('Opened job page. Review and submit manually.');
    console.log('Close browser when done.');
    
    await new Promise(resolve => browser.on('disconnected', resolve));
    return { success: true, message: 'manual_submit_expected' };
  } catch (err) {
    await browser.close();
    return { success: false, message: err.message };
  }
}

if (require.main === module) {
  runJobApply();
  app.listen(process.env.PORT || 3001, () => 
    console.log('API running on port', process.env.PORT || 3001)
  );
}

module.exports = { app, runJobApply };
```

### 2. google-sheets-helper.js
```javascript
const { google } = require('googleapis');

async function appendToSheet({spreadsheetId, keyFile, row}) {
  const auth = new google.auth.GoogleAuth({
    keyFile,
    scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });
  const client = await auth.getClient();
  const sheets = google.sheets({version:'v4', auth: client});
  await sheets.spreadsheets.values.append({
    spreadsheetId,
    range: 'Sheet1!A1',
    valueInputOption: 'USER_ENTERED',
    requestBody: { values: [row] }
  });
}

module.exports = { appendToSheet };
```

### 3. linkedin-runner.js
```javascript
const puppeteer = require('puppeteer');

async function runLinkedInEasyApply({jobUrl, resumePath, coverLetter}) {
  const browser = await puppeteer.launch({ 
    headless: process.env.HEADLESS !== 'false', 
    args:['--no-sandbox'] 
  });
  const page = await browser.newPage();
  
  try{
    await page.goto(jobUrl, { waitUntil:'networkidle2', timeout:60000 });

    // Wait for Easy Apply button
    const easyApply = await page.$x("//button[contains(., 'Easy Apply') or contains(., 'Apply on LinkedIn')]");
    if(easyApply.length) { 
      await easyApply[0].click(); 
      await page.waitForTimeout(1200); 
    }

    // Fill resume
    const fileInput = await page.$('input[type="file"]');
    if (fileInput && resumePath) {
      await fileInput.uploadFile(resumePath);
      await page.waitForTimeout(800);
    }

    // Fill cover letter
    const textareas = await page.$$('textarea');
    if (textareas.length) {
      await textareas[0].focus();
      await textareas[0].type(coverLetter.slice(0,1000));
    }

    console.log('LinkedIn filled — review modal and click Submit manually.');
    console.log('Leaving browser open. Close when done.');
    await new Promise(resolve => browser.on('disconnected', resolve));
    return { success: true, message: 'manual_submit_expected' };
  }catch(err){
    await browser.close();
    return { success:false, message: err.message };
  }
}

module.exports = { runLinkedInEasyApply };
```

### 4. greenhouse-runner.js
```javascript
const puppeteer = require('puppeteer');

async function runGreenhouseApply({jobUrl, resumePath, coverLetter}) {
  const browser = await puppeteer.launch({ 
    headless: process.env.HEADLESS !== 'false', 
    args:['--no-sandbox'] 
  });
  const page = await browser.newPage();
  
  try{
    await page.goto(jobUrl, { waitUntil:'networkidle2', timeout:60000 });

    // Find Apply button
    const apply = await page.$x("//a[contains(., 'Apply') or contains(., 'Apply now')]");
    if (apply.length) { 
      await apply[0].click(); 
      await page.waitForTimeout(1200); 
    }

    // Upload resume
    const resumeInput = await page.$('input[type="file"][name*="resume"], input[type="file"]');
    if (resumeInput && resumePath) await resumeInput.uploadFile(resumePath);

    // Fill cover letter
    const cover = await page.$('textarea[name*="cover"], textarea');
    if (cover) { 
      await cover.focus(); 
      await cover.type(coverLetter.slice(0,2000)); 
    }

    console.log('Greenhouse form filled — review and submit manually.');
    await new Promise(resolve => browser.on('disconnected', resolve));
    return { success: true, message: 'manual_submit_expected' };
  }catch(err){
    await browser.close();
    return { success:false, message: err.message };
  }
}

module.exports = { runGreenhouseApply };
```

## 🚀 Quick Start

1. Copy all files above into your `backend/` folder
2. Run: `cd backend && npm install`
3. Create `.env` from `.env.example` and add your OpenAI key
4. Run: `npm start`
5. API will be available at http://localhost:3001

## ✅ System Features

- **Semi-Automatic Mode**: Browser opens visibly, fills forms, waits for your manual submit
- **No CAPTCHA Bypass**: You solve CAPTCHAs manually = TOS compliant
- **History Tracking**: JSON + optional Google Sheets
- **Site-Specific Runners**: LinkedIn & Greenhouse examples included
- **API Endpoints**: Frontend can sync with `/history` and `/push-history`

## 📅 Next Steps

See main repository README for:
- GitHub Actions daily scheduler setup
- Frontend integration
- Google Sheets dashboard
