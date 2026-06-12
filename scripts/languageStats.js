/**
 * § 06 · Instrument panel — language distribution and profile counters.
 *
 * Aggregates language bytes across all non-fork repos, pulls follower /
 * star / streak counters, and renders readme-assets/languages.svg.
 *
 * CLI: node scripts/languageStats.js
 */
require('dotenv').config({ quiet: true });
const fs = require('fs');
const path = require('path');
const {
  GOLD,
  GOLD_BRIGHT,
  GOLD_DEEP,
  BRASS,
  BG,
  BG_PANEL,
  INK_DIM,
  INK_MID,
  FONT_SERIF,
  FONT_MONO
} = require('../src/voyagerConstants');
const { generateStars, formatNumber } = require('./generateAll');
const github = require('../src/utils/github');

const CACHE_PATH = path.join(__dirname, '../data/cache/instruments.json');
const SVG_PATH = path.join(__dirname, '../readme-assets/languages.svg');
const DEFAULT_OWNER = 'DeepExtrema';
const MAX_LANGS = 6;

// Gold ramp, brightest segment first.
const SEGMENT_COLORS = [GOLD_BRIGHT, GOLD, BRASS, GOLD_DEEP, '#5a4220', '#3a2c14', '#241b0c'];

const token = process.env.GITHUB_TOKEN;
let octokit = null;
if (token) {
  const { Octokit } = require('@octokit/rest');
  octokit = new Octokit({ auth: token });
}

function loadCache() {
  if (!fs.existsSync(CACHE_PATH)) return null;
  try {
    return JSON.parse(fs.readFileSync(CACHE_PATH, 'utf8'));
  } catch (e) {
    return null;
  }
}

function saveCache(data) {
  fs.mkdirSync(path.dirname(CACHE_PATH), { recursive: true });
  fs.writeFileSync(CACHE_PATH, JSON.stringify(data, null, 2), 'utf8');
}

/** Collapses raw byte counts into the top N languages plus OTHER, as percentages. */
function toPercentages(byteTotals, maxLangs = MAX_LANGS) {
  const entries = Object.entries(byteTotals).sort((a, b) => b[1] - a[1]);
  const totalBytes = entries.reduce((acc, [, bytes]) => acc + bytes, 0);
  if (totalBytes === 0) return [];

  const top = entries.slice(0, maxLangs);
  const restBytes = entries.slice(maxLangs).reduce((acc, [, bytes]) => acc + bytes, 0);

  const langs = top.map(([name, bytes]) => ({
    name,
    percent: (bytes / totalBytes) * 100
  }));
  if (restBytes > 0) {
    langs.push({ name: 'OTHER', percent: (restBytes / totalBytes) * 100 });
  }
  return langs;
}

/** Longest run of consecutive contribution days in the calendar. */
function longestStreak(weeks) {
  const days = [];
  for (const week of weeks || []) {
    days.push(...(week.contributionDays || []));
  }
  days.sort((a, b) => new Date(a.date) - new Date(b.date));
  let max = 0;
  let current = 0;
  for (const day of days) {
    if ((day.contributionCount || 0) > 0) {
      current += 1;
      if (current > max) max = current;
    } else {
      current = 0;
    }
  }
  return max;
}

async function gatherStats(owner) {
  if (!token) {
    console.error('No GITHUB_TOKEN — falling back to cache for instrument panel.');
    const cached = loadCache();
    if (cached) return cached;
    return {
      langs: [
        { name: 'Python', percent: 46 },
        { name: 'TypeScript', percent: 22 },
        { name: 'JavaScript', percent: 14 },
        { name: 'Rust', percent: 8 },
        { name: 'Swift', percent: 6 },
        { name: 'OTHER', percent: 4 }
      ],
      followers: 0,
      totalStars: 0,
      repoCount: 0,
      streak: 0
    };
  }

  const { data: user } = await octokit.rest.users.getByUsername({ username: owner });

  const { data: reposData } = await octokit.rest.repos.listForUser({
    username: owner,
    type: 'owner',
    per_page: 100
  });
  const repos = reposData.filter(r => !r.fork);

  const byteTotals = {};
  for (const repo of repos) {
    try {
      const { data: langs } = await octokit.rest.repos.listLanguages({ owner, repo: repo.name });
      for (const [lang, bytes] of Object.entries(langs)) {
        byteTotals[lang] = (byteTotals[lang] || 0) + bytes;
      }
    } catch (e) {
      console.error(`Could not fetch languages for ${repo.name}: ${e.message}`);
    }
  }

  const calendar = await github.getContributionCalendar(owner);

  const stats = {
    langs: toPercentages(byteTotals),
    followers: user.followers || 0,
    totalStars: repos.reduce((acc, r) => acc + (r.stargazers_count || 0), 0),
    repoCount: repos.length,
    streak: longestStreak(calendar.weeks)
  };
  saveCache({ ...stats, timestamp: new Date().toISOString() });
  return stats;
}

function renderInstrumentsSvg(stats) {
  const BAR_X = 36;
  const BAR_Y = 84;
  const BAR_W = 1128;
  const BAR_H = 16;

  const segments = [];
  const legend = [];
  let cursor = BAR_X;
  let legendX = BAR_X;
  stats.langs.forEach((lang, i) => {
    const w = (lang.percent / 100) * BAR_W;
    const color = SEGMENT_COLORS[i % SEGMENT_COLORS.length];
    segments.push(`    <rect x="${cursor.toFixed(1)}" y="${BAR_Y}" width="${Math.max(w, 1).toFixed(1)}" height="${BAR_H}" fill="${color}"/>`);
    cursor += w;

    const label = `${lang.name.toUpperCase()} ${lang.percent.toFixed(1)}%`;
    legend.push(`    <g transform="translate(${legendX.toFixed(0)} 0)">
      <rect y="-8" width="10" height="10" fill="${color}"/>
      <text x="18" fill="${INK_MID}">${label}</text>
    </g>`);
    legendX += 18 + label.length * 7.2 + 34;
  });

  const counters = [
    { label: 'FOLLOWERS', value: formatNumber(stats.followers) },
    { label: 'STARS · TOTAL', value: formatNumber(stats.totalStars) },
    { label: 'PUBLIC REPOS', value: formatNumber(stats.repoCount) },
    { label: 'LONGEST STREAK', value: `${stats.streak}`, suffix: ' DAYS' }
  ];
  const counterGroups = counters.map((c, i) => {
    const x = 36 + i * 290;
    const suffix = c.suffix ? `<tspan font-size="12" fill="${INK_DIM}" font-family="${FONT_MONO}" letter-spacing="2">${c.suffix}</tspan>` : '';
    return `  <g transform="translate(${x} 196)" font-family="${FONT_MONO}" font-size="10" letter-spacing="2">
    <text fill="${INK_DIM}">${c.label}</text>
    <text y="32" font-family="${FONT_SERIF}" font-size="26" fill="${GOLD_BRIGHT}" font-weight="500" letter-spacing="0">${c.value}${suffix}</text>
  </g>`;
  }).join('\n');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 280" width="1200" height="280">
  <rect width="1200" height="280" fill="${BG}"></rect>
  ${generateStars(1200, 280, 14, 23)}

  <g font-family="${FONT_MONO}" font-size="11" fill="${GOLD}" letter-spacing="3">
    <text x="36" y="36">§ 06  ·  INSTRUMENT  PANEL  ·  LANGUAGE  DISTRIBUTION</text>
    <text x="1164" y="36" text-anchor="end" fill="${INK_DIM}">BYTES · ALL REPOS</text>
  </g>

  <g>
    <rect x="${BAR_X - 1}" y="${BAR_Y - 1}" width="${BAR_W + 2}" height="${BAR_H + 2}" fill="none" stroke="${BG_PANEL}" stroke-width="1"/>
${segments.join('\n')}
  </g>

  <g transform="translate(0 134)" font-family="${FONT_MONO}" font-size="9" letter-spacing="1.5">
${legend.join('\n')}
  </g>

  <line x1="36" y1="166" x2="1164" y2="166" stroke="${BG_PANEL}" stroke-dasharray="2 3"/>

${counterGroups}
</svg>`;
}

async function main() {
  console.error('🛠 Generating instrument panel (language stats)...');
  const stats = await gatherStats(DEFAULT_OWNER);
  fs.mkdirSync(path.dirname(SVG_PATH), { recursive: true });
  fs.writeFileSync(SVG_PATH, renderInstrumentsSvg(stats), 'utf8');
  console.error('✅ Generated languages.svg');
}

module.exports = {
  toPercentages,
  longestStreak,
  renderInstrumentsSvg,
  main
};

if (require.main === module) {
  main().catch(err => {
    console.error('Fatal error generating instrument panel:', err);
    process.exit(1);
  });
}
