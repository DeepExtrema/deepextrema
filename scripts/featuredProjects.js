/**
 * § 02 · Notable instruments — featured-projects grid.
 *
 * Reads the curated list in data/featured.yaml, fetches live stats
 * (stars, language, last push) from the GitHub API, and renders
 * readme-assets/featured.svg plus the FEATURED section of README.md.
 *
 * CLI: node scripts/featuredProjects.js
 */
require('dotenv').config({ quiet: true });
const fs = require('fs');
const path = require('path');
const {
  GOLD,
  GOLD_BRIGHT,
  GOLD_DEEP,
  BG,
  BG_PANEL,
  INK_DIM,
  INK_MID,
  FONT_SERIF,
  FONT_MONO
} = require('../src/voyagerConstants');
const { injectMarkdown, generateStars, formatNumber } = require('./generateAll');

const FEATURED_YAML = path.join(__dirname, '../data/featured.yaml');
const CACHE_PATH = path.join(__dirname, '../data/cache/featured.json');
const SVG_PATH = path.join(__dirname, '../readme-assets/featured.svg');
const README_PATH = path.join(__dirname, '../README.md');
const DEFAULT_OWNER = 'DeepExtrema';

const token = process.env.GITHUB_TOKEN;
let octokit = null;
if (token) {
  const { Octokit } = require('@octokit/rest');
  octokit = new Octokit({ auth: token });
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** Parses the simple `repo: tagline` lines of featured.yaml, preserving order. */
function loadFeaturedList() {
  const entries = [];
  if (!fs.existsSync(FEATURED_YAML)) return entries;
  const lines = fs.readFileSync(FEATURED_YAML, 'utf8').split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const idx = trimmed.indexOf(':');
    if (idx === -1) continue;
    entries.push({
      name: trimmed.substring(0, idx).trim(),
      tagline: trimmed.substring(idx + 1).trim()
    });
  }
  return entries;
}

function relativeAge(isoDate) {
  if (!isoDate) return 'UNKNOWN';
  const days = Math.floor((Date.now() - new Date(isoDate).getTime()) / 86400000);
  if (days <= 0) return 'TODAY';
  if (days < 30) return `${days}D AGO`;
  if (days < 365) return `${Math.floor(days / 30)}MO AGO`;
  return `${Math.floor(days / 365)}Y AGO`;
}

async function fetchStats(entries, owner) {
  if (!token) {
    console.error('No GITHUB_TOKEN — falling back to cache for featured stats.');
    const cached = loadFromCache();
    if (cached) return cached;
    return entries.map(e => ({ ...e, stars: 0, language: 'TEXT', pushed_at: null }));
  }

  const results = [];
  for (const entry of entries) {
    try {
      const { data } = await octokit.rest.repos.get({ owner, repo: entry.name });
      results.push({
        ...entry,
        stars: data.stargazers_count || 0,
        language: data.language || 'TEXT',
        pushed_at: data.pushed_at || null
      });
    } catch (e) {
      console.error(`Could not fetch ${owner}/${entry.name}: ${e.message}`);
      results.push({ ...entry, stars: 0, language: 'TEXT', pushed_at: null });
    }
  }
  fs.mkdirSync(path.dirname(CACHE_PATH), { recursive: true });
  fs.writeFileSync(CACHE_PATH, JSON.stringify({ projects: results, timestamp: new Date().toISOString() }, null, 2), 'utf8');
  return results;
}

function loadFromCache() {
  if (!fs.existsSync(CACHE_PATH)) return null;
  try {
    const cache = JSON.parse(fs.readFileSync(CACHE_PATH, 'utf8'));
    return Array.isArray(cache.projects) ? cache.projects : null;
  } catch (e) {
    return null;
  }
}

/** Wraps a tagline into at most two lines of roughly maxLen characters. */
function wrapTagline(text, maxLen = 44) {
  if (!text) return ['', ''];
  if (text.length <= maxLen) return [text, ''];
  let breakIdx = text.lastIndexOf(' ', maxLen);
  if (breakIdx === -1) breakIdx = maxLen;
  const line1 = text.substring(0, breakIdx).trim();
  let line2 = text.substring(breakIdx).trim();
  if (line2.length > maxLen) line2 = line2.substring(0, maxLen - 1).trim() + '…';
  return [line1, line2];
}

function renderFeaturedSvg(projects) {
  const CARD_W = 364;
  const CARD_H = 168;
  const XS = [36, 418, 800];
  const YS = [64, 254];

  const cards = projects.slice(0, 6).map((p, i) => {
    const x = XS[i % 3];
    const y = YS[Math.floor(i / 3)];
    const idx = String(i + 1).padStart(2, '0');
    const [line1, line2] = wrapTagline(p.tagline);
    const statsStr = `${(p.language || 'TEXT').toUpperCase()} · ${formatNumber(p.stars || 0)}★ · ${relativeAge(p.pushed_at)}`;
    return `  <g transform="translate(${x} ${y})">
    <rect width="${CARD_W}" height="${CARD_H}" fill="${BG_PANEL}" fill-opacity="0.45" stroke="${GOLD_DEEP}" stroke-width="0.8" rx="4"/>
    <text x="22" y="32" font-family="${FONT_MONO}" font-size="9" fill="${GOLD}" letter-spacing="3">${idx} ▸ INSTRUMENT</text>
    <text x="22" y="64" font-family="${FONT_SERIF}" font-size="21" fill="${GOLD_BRIGHT}" font-weight="500">${escapeXml(p.name)}</text>
    <text x="22" y="92" font-family="${FONT_SERIF}" font-size="12.5" fill="${INK_MID}" font-style="italic">${escapeXml(line1)}</text>
    <text x="22" y="110" font-family="${FONT_SERIF}" font-size="12.5" fill="${INK_MID}" font-style="italic">${escapeXml(line2)}</text>
    <text x="22" y="144" font-family="${FONT_MONO}" font-size="9" fill="${INK_DIM}" letter-spacing="2">${escapeXml(statsStr)}</text>
  </g>`;
  }).join('\n');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 460" width="1200" height="460">
  <rect width="1200" height="460" fill="${BG}"></rect>
  ${generateStars(1200, 460, 16, 7)}

  <g font-family="${FONT_MONO}" font-size="11" fill="${GOLD}" letter-spacing="3">
    <text x="36" y="36">§ 02  ·  NOTABLE  INSTRUMENTS</text>
    <text x="1164" y="36" text-anchor="end" fill="${INK_DIM}">CURATED · LIVE STATS</text>
  </g>

${cards}
</svg>`;
}

function buildReadmeSection(projects, owner) {
  const links = projects.slice(0, 6)
    .map(p => `[${p.name}](https://github.com/${owner}/${p.name})`)
    .join('  ·  ');
  return `<div align="center">
  <img src="readme-assets/featured.svg" alt="Notable instruments — featured projects" width="100%">
</div>

<div align="center">
<sub>OPEN AN INSTRUMENT · ${links}</sub>
</div>`;
}

async function main() {
  console.error('🛠 Generating featured projects (Notable instruments)...');
  const entries = loadFeaturedList();
  if (entries.length === 0) {
    console.error('⚠️ No entries in data/featured.yaml — nothing to do.');
    return;
  }

  const projects = await fetchStats(entries, DEFAULT_OWNER);

  fs.mkdirSync(path.dirname(SVG_PATH), { recursive: true });
  fs.writeFileSync(SVG_PATH, renderFeaturedSvg(projects), 'utf8');
  console.error('✅ Generated featured.svg');

  if (fs.existsSync(README_PATH)) {
    const readme = fs.readFileSync(README_PATH, 'utf8');
    const updated = injectMarkdown(readme, 'FEATURED', buildReadmeSection(projects, DEFAULT_OWNER));
    fs.writeFileSync(README_PATH, updated, 'utf8');
    console.error('✅ Injected FEATURED section in README.');
  }
}

module.exports = {
  loadFeaturedList,
  wrapTagline,
  relativeAge,
  renderFeaturedSvg,
  buildReadmeSection,
  main
};

if (require.main === module) {
  main().catch(err => {
    console.error('Fatal error generating featured projects:', err);
    process.exit(1);
  });
}
