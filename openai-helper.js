const OpenAI = require('openai');
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const COVER_PROMPT = `You are a professional career writer. Write a concise 3-paragraph cover letter tailored to the job description and candidate profile. Use examples from candidate profile and include why candidate fits. Job description: {JOB}\n\nCandidate profile: {PROFILE}\n\nTone: {TONE}`;

async function generateCoverLetter({jobDescription, candidateProfile, tone='professional'}) {
  const prompt = COVER_PROMPT
    .replace('{JOB}', jobDescription)
    .replace('{PROFILE}', JSON.stringify(candidateProfile, null, 2))
    .replace('{TONE}', tone);

  const res = await client.chat.completions.create({
    model: 'gpt-4o-mini', // or your preferred model
    messages: [{role:'user', content: prompt}],
    max_tokens: 500,
    temperature: 0.2
  });

  const text = res.choices?.[0]?.message?.content ?? '';
  return text.trim();
}

module.exports = { generateCoverLetter };
