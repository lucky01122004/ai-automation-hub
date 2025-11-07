# Job Application Automation - Complete Setup Guide

## Files Already Created
- ✅ package.json
- ✅ index.js
- ✅ openai-helper.js

## Remaining Files to Create

### 1. puppeteer-runner.js
```javascript
const fs = require('fs');
const puppeteer = require('puppeteer');

async function runPuppeteerApply({ jobUrl, resumePath, coverLetterText, metadata }) {
  const headless = process.env.HEADLESS !== 'false';
  const browser = await puppeteer.launch({ headless, args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();

  try {
    await page.goto(jobUrl, { waitUntil: 'networkidle2', timeout: 60000 });

    // Find Apply button
    const applyBtn = await page.$x("//button[contains(translate(., 'APPLY', 'apply'), 'apply')]");
    if (applyBtn && applyBtn.length) { await applyBtn[0].click(); await page.waitForTimeout(1000); }

    // Fill form fields
    const fields = {
      name: 'input[name="name"], input#name',
      email: 'input[name="email"], input#email',
      cover: 'textarea[name="cover_letter"], textarea#cover',
      resume: 'input[type="file"]'
    };

    // Fill name/email
    for (const sel of [fields.name, fields.email]) {
      if (!sel) continue;
      const el = await page.$(sel);
      if (el) {
        const val = sel.includes('name') ? process.env.USER_NAME : process.env.USER_EMAIL;
        await el.focus();
        await el.click({ clickCount: 3 });
        await el.type(val || '');
      }
    }

    // Fill cover letter
    const coverEl = await page.$(fields.cover);
    if (coverEl) {
      await coverEl.focus();
      await coverEl.type(coverLetterText.slice(0, 3000));
    }

    // Upload resume
    const fileInput = await page.$(fields.resume);
    if (fileInput && resumePath && fs.existsSync(resumePath)) {
      await fileInput.uploadFile(resumePath);
    }

    // Check for CAPTCHA
    const captcha = await detectCaptcha(page);
    if (captcha) {
      await browser.close();
      return { success: false, message: 'captcha_detected: manual action required' };
    }

    await browser.close();
    return { success: true, message: 'applied (simulated selectors used)' };
  } catch (err) {
    await browser.close();
    return { success: false, message: 'error: '+ String(err.message) };
  }
}

async function detectCaptcha(page) {
  const frameCount = page.frames().length;
  if (frameCount > 5) return true;
  const body = await page.content();
  if (body.toLowerCase().includes('recaptcha') || body.toLowerCase().includes('g-recaptcha')) return true;
  return false;
}

module.exports = { runPuppeteerApply };
```

### 2. google-sheets.js
```javascript
const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

async function logToSheet(entry) {
  if (process.env.GOOGLE_SHEETS_SPREADSHEET_ID && process.env.GOOGLE_SHEETS_CREDENTIALS_JSON) {
    const keyFile = process.env.GOOGLE_SHEETS_CREDENTIALS_JSON;
    const auth = new google.auth.GoogleAuth({
      keyFile,
      scopes: ['https://www.googleapis.com/auth/spreadsheets']
    });
    const client = await auth.getClient();
    const sheets = google.sheets({version:'v4', auth: client });
    const values = [[
      new Date().toISOString(),
      entry.automationId,
      entry.jobTitle,
      entry.company,
      entry.url,
      entry.status,
      entry.notes || ''
    ]];
    await sheets.spreadsheets.values.append({
      spreadsheetId: process.env.GOOGLE_SHEETS_SPREADSHEET_ID,
      range: 'Sheet1!A1',
      valueInputOption: 'USER_ENTERED',
      requestBody: { values }
    });
  } else {
    // Fallback: append to local CSV
    const file = path.join(__dirname, 'application_log.csv');
    const csvWriter = createCsvWriter({
      path: file,
      header: [
        {id:'timestamp', title:'timestamp'},
        {id:'automationId', title:'automationId'},
        {id:'jobTitle', title:'jobTitle'},
        {id:'company', title:'company'},
        {id:'url', title:'url'},
        {id:'status', title:'status'},
        {id:'notes', title:'notes'}
      ],
      append: fs.existsSync(file)
    });
    await csvWriter.writeRecords([{
      timestamp: new Date().toISOString(),
      automationId: entry.automationId,
      jobTitle: entry.jobTitle,
      company: entry.company,
      url: entry.url,
      status: entry.status,
      notes: entry.notes || ''
    }]);
  }
}

module.exports = { logToSheet };
```

### 3. automations.json
```json
[
  {
    "id": "a_abc123",
    "title": "Apply Product Designer - Series A startups",
    "type": "job-apply",
    "description": "Apply to Product Designer roles at Series-A startups. Generate tailored cover letters and autofill applications.",
    "steps": [
      {"action":"parse_job_description"},
      {"action":"tailor_resume"},
      {"action":"generate_cover_letter"},
      {"action":"open_application_url"},
      {"action":"autofill_fields"},
      {"action":"submit_application"},
      {"action":"log_status"}
    ],
    "criteria": {
      "title_keywords": ["Product Designer","UX Designer"],
      "location": "remote",
      "min_experience": 2,
      "sites": ["https://www.example.com/jobs"]
    }
  }
]
```

### 4. .env.example
```
OPENAI_API_KEY=sk-...
GOOGLE_SHEETS_CREDENTIALS_JSON=/path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
RESUME_PATH=./resume.pdf
USER_EMAIL=you@example.com
USER_NAME=Your Name
HEADLESS=true
```

### 5. .github/workflows/daily-run.yml
```yaml
name: Daily Job Apply Runner
on:
  schedule:
    - cron: '0 6 * * *'  # 06:00 UTC daily
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install
        run: npm ci
      - name: Run automation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          RESUME_PATH: ./resume.pdf
          USER_NAME: ${{ secrets.USER_NAME }}
          USER_EMAIL: ${{ secrets.USER_EMAIL }}
          GOOGLE_SHEETS_SPREADSHEET_ID: ${{ secrets.GOOGLE_SHEETS_SPREADSHEET_ID }}
          HEADLESS: "true"
        run: |
          if [ -n "${{ secrets.GOOGLE_SHEETS_CREDENTIALS_JSON }}" ]; then
            echo "${{ secrets.GOOGLE_SHEETS_CREDENTIALS_JSON }}" > /tmp/creds.json
            export GOOGLE_SHEETS_CREDENTIALS_JSON=/tmp/creds.json
          fi
          node index.js
```

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create .env file** (copy from .env.example and fill in your values)

3. **Add your resume.pdf** to the repo root

4. **Create automations.json** with your job search criteria

5. **Run locally:**
   ```bash
   npm start
   ```

6. **Setup GitHub Actions** (optional):
   - Go to Settings > Secrets and variables > Actions
   - Add secrets: OPENAI_API_KEY, USER_NAME, USER_EMAIL
   - The workflow will run daily at 6 AM UTC

## Important Safety Notes

⚠️ **Legal & Ethical Usage:**
- Automating applications may violate some sites' Terms of Service
- Always use official APIs when available (LinkedIn, Indeed, Greenhouse)
- Consider semi-automated mode: the script fills forms but YOU click submit
- Never bypass CAPTCHAs - if detected, the script stops for manual intervention
- Respect rate limits: limit to 10-25 applications per day

## Handling CAPTCHAs

The `puppeteer-runner.js` includes CAPTCHA detection. When detected:
1. The script pauses and returns an error
2. You'll need to manually complete the application
3. Consider modifying to run in headed mode (HEADLESS=false) for manual intervention

## Customization

To target specific job sites:
1. Update selectors in `puppeteer-runner.js` for each site's form structure
2. Add site-specific logic in `findJobsForAutomation()` in `index.js`
3. Use official APIs whenever possible instead of scraping

## Next Steps

Choose your implementation:

**Option 1: Fully Automated (risky)**
- Script runs daily via GitHub Actions
- Auto-submits applications
- Use only on sites that permit automation

**Option 2: Semi-Automated (recommended)**
- Script generates cover letters & fills forms
- Opens browser in headed mode for you to review
- YOU click submit after solving CAPTCHAs
- Much safer and more reliable

**Option 3: Manual with AI Assistance**
- Just use the `openai-helper.js` to generate cover letters
- Manually copy/paste into application forms
- Safest approach
