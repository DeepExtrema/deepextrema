require('dotenv').config();
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
  INK,
  INK_BRIGHT,
  FONT_SERIF,
  FONT_MONO
} = require('../src/voyagerConstants');

const token = process.env.GITHUB_TOKEN;
let octokitInstance = null;

function getOctokit() {
  if (!octokitInstance && token) {
    const { Octokit } = require('@octokit/rest');
    octokitInstance = new Octokit({ auth: token });
  }
  return octokitInstance;
}

// Helper: Seeded Random Generator
function createSeededRandom(seed) {
  let s = seed;
  return function() {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

// Helper: Generate Stars (Voyager space noise background)
function generateStars(width, height, count = 12, seed = 0) {
  const random = createSeededRandom(seed);
  const pts = [];
  const GOLD_COLOR = "#d4a85a";
  for (let i = 0; i < count; i++) {
    const x = Math.floor(random() * (width + 1));
    const y = Math.floor(random() * (height + 1));
    const radii = [0.5, 0.6, 0.7, 0.8];
    const r = radii[Math.floor(random() * radii.length)];
    const op = 0.35 + random() * (0.6 - 0.35);
    pts.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${GOLD_COLOR}" opacity="${op.toFixed(2)}"/>`);
  }
  return `<g class="stars">${pts.join('')}</g>`;
}

// Helper: Truncate String
function truncateString(s, maxLength = 50, suffix = "...") {
  if (!s) return "";
  if (s.length <= maxLength) return s;
  return s.slice(0, maxLength - suffix.length) + suffix;
}

// Helper: Format large numbers (K/M suffixes)
function formatNumber(n) {
  if (n >= 1000000) {
    return `${(n / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
  } else if (n >= 1000) {
    return `${(n / 1000).toFixed(1).replace(/\.0$/, '')}K`;
  }
  return String(n);
}

// Helper: Load Cache
function loadCache(name) {
  const cachePath = path.join(__dirname, '../data/cache', `${name}.json`);
  if (fs.existsSync(cachePath)) {
    try {
      return JSON.parse(fs.readFileSync(cachePath, 'utf8'));
    } catch (e) {
      console.error(`Error reading cache ${name}:`, e);
    }
  }
  return null;
}

// Helper: Save Cache
function saveCache(name, data) {
  const cachePath = path.join(__dirname, '../data/cache', `${name}.json`);
  try {
    fs.mkdirSync(path.dirname(cachePath), { recursive: true });
    fs.writeFileSync(cachePath, JSON.stringify(data, null, 2), 'utf8');
  } catch (e) {
    console.error(`Error writing cache ${name}:`, e);
  }
}

// Helper: Get Calendar Week Number
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// Helper: Split description for current transmissions SVG columns
function splitDescription(desc, maxLen = 35) {
  if (!desc) return ["", ""];
  if (desc.length <= maxLen) return [desc, ""];
  const idx = desc.lastIndexOf(" ", maxLen);
  if (idx === -1) {
    return [desc.substring(0, maxLen), desc.substring(maxLen, maxLen * 2)];
  }
  return [desc.substring(0, idx).trim(), desc.substring(idx).trim().substring(0, maxLen)];
}

// Get Authenticated user or default to DeepExtrema
async function getOwner(defaultOwner = 'DeepExtrema') {
  if (!token) {
    return defaultOwner;
  }
  try {
    const { data } = await octokit.rest.users.getAuthenticated();
    return data.login;
  } catch (e) {
    console.warn("Could not get authenticated user. Using default owner:", defaultOwner);
    return defaultOwner;
  }
}

// Fetch repositories, count commits and open PRs for scoring
async function getReposForScoring(owner) {
  if (!token) {
    return [
      {
        name: "cosmic-cockpit",
        description: "Self-updating profile pipeline. Pulls 7 sources every 6 hours.",
        stars: 248,
        language: "Python",
        commits_30d: 47,
        commits_14d: 15,
        open_prs: 1,
        archived: false,
        score: 15 * 3 + 1 * 2
      },
      {
        name: "extrema-ml",
        description: "Time-series anomaly detection. Online, no GPU required.",
        stars: 612,
        language: "Python",
        commits_30d: 28,
        commits_14d: 10,
        open_prs: 2,
        archived: false,
        score: 10 * 3 + 2 * 2
      },
      {
        name: "orbital-tooling",
        description: "Edge-deploy primitives. Low-bandwidth, high-latency.",
        stars: 184,
        language: "Rust",
        commits_30d: 19,
        commits_14d: 5,
        open_prs: 0,
        archived: false,
        score: 5 * 3 + 0 * 2
      }
    ];
  }

  try {
    let reposData = [];
    try {
      const response = await octokit.rest.repos.listForUser({
        username: owner,
        type: 'owner',
        per_page: 100
      });
      reposData = response.data;
    } catch (err) {
      const response = await octokit.rest.repos.listForOrg({
        org: owner,
        per_page: 100
      });
      reposData = response.data;
    }

    const nonForkRepos = reposData.filter(r => !r.fork);
    const cutoff14 = new Date();
    cutoff14.setDate(cutoff14.getDate() - 14);
    const cutoff30 = new Date();
    cutoff30.setDate(cutoff30.getDate() - 30);

    const results = [];
    for (const r of nonForkRepos) {
      let commits14d = 0;
      let commits30d = 0;
      try {
        const response = await octokit.rest.repos.listCommits({
          owner,
          repo: r.name,
          since: cutoff30.toISOString(),
          per_page: 100
        });
        const commitDates = response.data.map(c => new Date(c.commit.author?.date || c.commit.committer?.date));
        commits30d = commitDates.length;
        commits14d = commitDates.filter(d => d >= cutoff14).length;
      } catch (e) {
        // Ignore
      }

      let open_prs = 0;
      try {
        const pullsResponse = await octokit.rest.pulls.list({
          owner,
          repo: r.name,
          state: 'open',
          per_page: 100
        });
        open_prs = pullsResponse.data.length;
      } catch (e) {
        // Ignore
      }

      const score = commits14d * 3 + open_prs * 2;

      results.push({
        name: r.name,
        description: r.description || "No description provided.",
        stars: r.stargazers_count || 0,
        language: r.language || "TEXT",
        commits_30d: commits30d,
        commits_14d: commits14d,
        open_prs,
        archived: !!r.archived,
        score
      });
    }

    results.sort((a, b) => b.score - a.score);
    return results;
  } catch (e) {
    console.error("Error fetching/scoring repositories, using cache fallback:", e);
    const cache = loadCache("current_focus");
    if (cache && Array.isArray(cache.top_3)) {
      return cache.top_3;
    }
    // Static fallback
    return [
      {
        name: "cosmic-cockpit",
        description: "Self-updating profile pipeline. Pulls 7 sources every 6 hours.",
        stars: 248,
        language: "Python",
        commits_30d: 47,
        commits_14d: 15,
        open_prs: 1,
        archived: false,
        score: 15 * 3 + 1 * 2
      },
      {
        name: "extrema-ml",
        description: "Time-series anomaly detection. Online, no GPU required.",
        stars: 612,
        language: "Python",
        commits_30d: 28,
        commits_14d: 10,
        open_prs: 2,
        archived: false,
        score: 10 * 3 + 2 * 2
      },
      {
        name: "orbital-tooling",
        description: "Edge-deploy primitives. Low-bandwidth, high-latency.",
        stars: 184,
        language: "Rust",
        commits_30d: 19,
        commits_14d: 5,
        open_prs: 0,
        archived: false,
        score: 5 * 3 + 0 * 2
      }
    ];
  }
}

// Markdown Injection Helper
function injectMarkdown(text, marker, newContent) {
  const startMarkerA = `<!-- ${marker}_START -->`;
  const endMarkerA = `<!-- ${marker}_END -->`;
  const startMarkerB = `<!-- ${marker} -->`;
  const endMarkerB = `<!-- /${marker} -->`;

  if (text.includes(startMarkerA) && text.includes(endMarkerA)) {
    const startIndex = text.indexOf(startMarkerA) + startMarkerA.length;
    const endIndex = text.indexOf(endMarkerA);
    return text.substring(0, startIndex) + `\n${newContent}\n` + text.substring(endIndex);
  }

  if (text.includes(startMarkerB) && text.includes(endMarkerB)) {
    const startIndex = text.indexOf(startMarkerB) + startMarkerB.length;
    const endIndex = text.indexOf(endMarkerB);
    return text.substring(0, startIndex) + `\n${newContent}\n` + text.substring(endIndex);
  }

  const regexA = new RegExp(`(<!--\\s*${marker}_START\\s*-->)[\\s\\S]*?(<!--\\s*${marker}_END\\s*-->)`, 'i');
  if (regexA.test(text)) {
    return text.replace(regexA, `$1\n${newContent}\n$2`);
  }

  const regexB = new RegExp(`(<!--\\s*${marker}\\s*-->)[\\s\\S]*?(<!--\\s*/${marker}\\s*-->)`, 'i');
  if (regexB.test(text)) {
    return text.replace(regexB, `$1\n${newContent}\n$2`);
  }

  return text;
}

// Signal Feed: Space Card (NASA APOD)
async function getSpaceSignal() {
  const nasaKey = process.env.NASA_API_KEY || "DEMO_KEY";
  try {
    const response = await fetch(`https://api.nasa.gov/planetary/apod?api_key=${nasaKey}`, { signal: AbortSignal.timeout(10000) });
    if (response.ok) {
      const data = await response.json();
      return {
        title: data.title || "Cosmic View",
        description: truncateString(data.explanation || "", 100),
        date: data.date || "",
        url: data.url || "",
        stale: false,
      };
    }
  } catch (e) {
    console.error("NASA API error:", e);
  }

  const cache = loadCache("signal_feed");
  if (cache && cache.space) {
    const cached = cache.space;
    cached.stale = true;
    return cached;
  }

  const facts = [
    { title: "Voyager 1", description: "The most distant human-made object, over 14 billion miles from Earth." },
    { title: "Neutron Stars", description: "A teaspoon of neutron star material weighs about 6 billion tons." },
    { title: "The Sun", description: "Light from the Sun takes about 8 minutes and 20 seconds to reach Earth." },
    { title: "Black Holes", description: "Time slows down near a black hole due to extreme gravitational effects." },
  ];
  const fact = facts[Math.floor(Math.random() * facts.length)];
  fact.stale = true;
  fact.date = new Date().toISOString().split('T')[0];
  return fact;
}

// Signal Feed: AI Card (HuggingFace Trending)
async function getAiSignal() {
  try {
    const response = await fetch("https://huggingface.co/api/trending", { signal: AbortSignal.timeout(10000) });
    if (response.ok) {
      const models = await response.json();
      if (models && models.length > 0) {
        const model = models[0];
        return {
          name: model.repoId || "Unknown",
          description: model.repoType || "model",
          url: `https://huggingface.co/${model.repoId || ''}`,
          stale: false,
        };
      }
    }
  } catch (e) {
    console.error("HuggingFace API error:", e);
  }

  if (token) {
    try {
      const response = await fetch("https://api.github.com/search/repositories?q=machine-learning+stars:>1000+pushed:>2024-01-01&sort=stars&per_page=5", {
        headers: {
          "Authorization": `token ${token}`,
          "User-Agent": "Voyager-Readme-Orchestrator"
        },
        signal: AbortSignal.timeout(10000)
      });
      if (response.ok) {
        const data = await response.json();
        const repos = data.items || [];
        if (repos.length > 0) {
          const repo = repos[Math.floor(Math.random() * Math.min(3, repos.length))];
          return {
            name: repo.full_name || "Unknown",
            description: truncateString(repo.description || "", 60),
            url: repo.html_url || "",
            stale: false,
          };
        }
      }
    } catch (e) {
      console.error("GitHub search error:", e);
    }
  }

  const cache = loadCache("signal_feed");
  if (cache && cache.ai) {
    const cached = cache.ai;
    cached.stale = true;
    return cached;
  }

  return {
    name: "Transformers",
    description: "State-of-the-art NLP library",
    url: "https://huggingface.co/docs/transformers",
    stale: true,
  };
}

// Signal Feed: Phrase Card (OpenAI or Curated)
async function getPhraseSignal() {
  const openaiKey = process.env.OPENAI_API_KEY;
  if (openaiKey) {
    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${openaiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [
            {
              role: "system",
              content: "You are a cosmic engineer's muse. Generate a single short, inspiring phrase (max 15 words) about exploration, building, or the frontier of technology. Be poetic but grounded. No quotes."
            },
            { role: "user", content: "Generate a phrase." }
          ],
          max_tokens: 50,
          temperature: 0.9,
        }),
        signal: AbortSignal.timeout(15000)
      });
      if (response.ok) {
        const data = await response.json();
        const phrase = data.choices[0].message.content.trim().replace(/^["']|["']$/g, '');
        return {
          text: phrase,
          source: "generated",
          stale: false,
        };
      }
    } catch (e) {
      console.error("OpenAI API error:", e);
    }
  }

  const phrases = [
    "Build for the timeline you want to live in.",
    "Depth first; scale later.",
    "The frontier rewards those who show up.",
    "Curiosity compounds like interest, but pays in discoveries.",
    "Ship early, iterate often, sleep eventually.",
    "Embrace the unknown, pioneer the next horizon.",
    "Every system starts as a question.",
    "Debug reality; deploy ambition.",
  ];

  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now - start;
  const oneDay = 1000 * 60 * 60 * 24;
  const dayOfYear = Math.floor(diff / oneDay);
  const dayIndex = dayOfYear % phrases.length;

  return {
    text: phrases[dayIndex],
    source: "curated",
    stale: false,
  };
}

// Main generation pipeline
async function main() {
  console.log("🚀 Starting Voyager Cockpit Generation Pipeline...");
  const currentNow = new Date();

  // Lazy load dependencies used inside main
  const React = require('react');
  const github = require('../src/utils/github');
  const { renderSvg } = require('../src/utils/satoriRenderer');
  const Timeline = require('../src/components/Timeline.jsx');
  const Heatmap = require('../src/components/Heatmap.jsx');

  // 1. Check if fast run
  const isFastRun = process.argv.includes('--fast') ||
                    (process.env.GITHUB_EVENT_SCHEDULE && process.env.GITHUB_EVENT_SCHEDULE !== '0 5 * * *');
  console.log(`Pipeline mode: ${isFastRun ? 'FAST (skip heavy SVGs)' : 'FULL (all assets)'}`);

  // 2. Fetch owner name
  const owner = await getOwner();
  console.log(`Target GitHub Owner: ${owner}`);

  // 3. GENERATE Header SVG
  try {
    const subtitlesPath = path.join(__dirname, '../data/subtitles.json');
    const headerPath = path.join(__dirname, '../readme-assets/header.svg');

    let subtitles = [
      "SIGNAL · OUTBOUND · PROFILE 01",
      "RECORD · GOLDEN · SIGNAL 02",
      "PARALLAX · SIGHTING · TRANS 03",
      "DEEP · FRONTIER · STATUS 04",
      "ORBITAL · TOOLING · BEACON 05",
      "CONSCIOUSNESS · FORWARD · PATH 06"
    ];
    if (fs.existsSync(subtitlesPath)) {
      try {
        subtitles = JSON.parse(fs.readFileSync(subtitlesPath, 'utf8'));
      } catch (e) {
        console.error("Error parsing subtitles.json:", e);
      }
    }
    const weekNum = getWeekNumber(currentNow);
    const subtitleIndex = weekNum % subtitles.length;
    const selectedSubtitle = subtitles[subtitleIndex];

    if (fs.existsSync(headerPath)) {
      let headerContent = fs.readFileSync(headerPath, 'utf8');
      const regex = /(<text\s+[^>]*letter-spacing="6"[^>]*>)([^<]*)(<\/text>)/i;
      if (regex.test(headerContent)) {
        headerContent = headerContent.replace(regex, `$1${selectedSubtitle}$3`);
        fs.writeFileSync(headerPath, headerContent, 'utf8');
        console.log(`✅ Generated header.svg with subtitle: ${selectedSubtitle}`);
      } else {
        console.warn("⚠️ Could not find subtitle placeholder in header.svg");
      }
    } else {
      console.warn(`⚠️ header.svg not found at ${headerPath}`);
    }
  } catch (e) {
    console.error("❌ Error generating header.svg:", e);
  }

  // 4. GENERATE Current Transmissions SVG
  let scoredRepos = [];
  try {
    const transmissionsPath = path.join(__dirname, '../readme-assets/current-transmissions.svg');
    const tagsPath = path.join(__dirname, '../data/focus_tags.yaml');
    
    // Load focus tags
    const tags = {};
    if (fs.existsSync(tagsPath)) {
      try {
        const content = fs.readFileSync(tagsPath, 'utf8');
        const lines = content.split('\n');
        for (const line of lines) {
          if (line.includes(':')) {
            const idx = line.indexOf(':');
            const k = line.substring(0, idx).trim().toLowerCase();
            const v = line.substring(idx + 1).trim();
            tags[k] = v;
          }
        }
      } catch (e) {
        console.error("Error reading focus_tags.yaml:", e);
      }
    }

    scoredRepos = await getReposForScoring(owner);
    // Cache the top 3 scored repos
    const top3 = scoredRepos.slice(0, 3);
    saveCache("current_focus", { top_3: top3, timestamp: currentNow.toISOString() });

    const nowUtc = `${String(currentNow.getUTCHours()).padStart(2, '0')}:${String(currentNow.getUTCMinutes()).padStart(2, '0')} UTC`;
    const colsSvg = [];
    const positions = [60, 450, 826];
    
    top3.forEach((repo, i) => {
      const posX = positions[i];
      const repoNameLower = repo.name.toLowerCase();
      const tag = tags[repoNameLower] || (i === 0 ? "PRIMARY" : "EXPERIMENT");
      const tagStr = `▸ ${tag}`;
      const [desc1, desc2] = splitDescription(repo.description);
      const lang = (repo.language || 'TEXT').toUpperCase();
      const starsCount = repo.stars || 0;
      const commits30 = repo.commits_30d || 0;
      const statusSuffix = repo.archived ? "ARCHIVED" : "LIVE";
      const statsStr = `${lang} · ${starsCount}★ · ${commits30} COMMITS · ${statusSuffix}`;
      
      const colSvg = `  <g transform="translate(${posX} 80)">
    <text font-family="${FONT_MONO}" font-size="9" fill="${GOLD}" letter-spacing="3">${tagStr}</text>
    <text y="32" font-family="${FONT_SERIF}" font-size="24" fill="${GOLD_BRIGHT}" font-weight="500">${repo.name}</text>
    <text y="62" font-family="${FONT_SERIF}" font-size="13" fill="${INK_MID}" font-style="italic">${desc1}</text>
    <text y="82" font-family="${FONT_SERIF}" font-size="13" fill="${INK_MID}" font-style="italic">${desc2}</text>
    <g font-family="${FONT_MONO}" font-size="9" fill="${INK_DIM}" letter-spacing="2">
      <text y="118">${statsStr}</text>
    </g>
  </g>`;
      colsSvg.push(colSvg);
    });

    const transmissionsSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220" width="1200" height="220">
  <rect width="1200" height="220" fill="${BG}"></rect>
  ${generateStars(1200, 220, 15, 10)}

  <g font-family="${FONT_MONO}" font-size="11" fill="${GOLD}" letter-spacing="3">
    <text x="36" y="32">§ 02  ·  CURRENT  TRANSMISSIONS</text>
    <text x="1164" y="32" text-anchor="end" fill="${INK_DIM}">REFRESHED · ${nowUtc}</text>
  </g>

  <!-- Dividers -->
  <g stroke="${BG_PANEL}" stroke-width="0.6">
    <line x1="424" y1="60" x2="424" y2="210"></line>
    <line x1="800" y1="60" x2="800" y2="210"></line>
  </g>

${colsSvg.join('\n')}
</svg>`;

    fs.writeFileSync(transmissionsPath, transmissionsSvg, 'utf8');
    console.log("✅ Generated current-transmissions.svg successfully.");
  } catch (e) {
    console.error("❌ Error generating current-transmissions.svg:", e);
  }

  // Pre-calculate recent commits and hourly commit clock distribution (useful for both heatmap and clock SVGs)
  let clockHours = Array(24).fill(0);
  let totalClockCommits = 0;
  if (!isFastRun) {
    try {
      const recentCommits = await github.getRecentCommits(owner, 90);
      recentCommits.forEach(c => {
        if (c.date) {
          const hr = new Date(c.date).getUTCHours();
          clockHours[hr]++;
        }
      });
      totalClockCommits = clockHours.reduce((a, b) => a + b, 0);
      saveCache("commit_clock", { hours: clockHours, timestamp: currentNow.toISOString() });
    } catch (e) {
      console.error("Error pre-calculating commits for clock, checking cache fallback:", e);
      const clockCache = loadCache("commit_clock");
      if (clockCache && Array.isArray(clockCache.hours)) {
        clockHours = clockCache.hours;
      } else {
        // Fallback distribution centered around 21:00 UTC
        clockHours = [
          30, 20, 10, 5, 2, 1, 1, 2, 5, 8, 12, 15,
          20, 18, 15, 22, 28, 35, 45, 60, 75, 85, 70, 50
        ];
      }
      totalClockCommits = clockHours.reduce((a, b) => a + b, 0);
    }
  }

  // 5. GENERATE Timeline SVG (Skip if fast)
  if (!isFastRun) {
    try {
      const timelinePath = path.join(__dirname, '../readme-assets/timeline.svg');
      const allRepos = await github.getRepos(owner);

      const mappedReposForTimeline = allRepos.map(r => ({
        name: r.name,
        created_at: r.created_at,
        pushed_at: r.pushed_at,
        archived: r.archived,
        stars: r.stars || r.stargazers_count || 0,
        language: r.language || 'TEXT'
      }));

      const timelineElement = React.createElement(Timeline, {
        repos: mappedReposForTimeline,
        minYear: 2021,
        maxYear: currentNow.getFullYear() + 1,
        now: currentNow.toISOString()
      });

      const timelineSvg = await renderSvg(timelineElement, 1200, 420);
      fs.writeFileSync(timelinePath, timelineSvg, 'utf8');
      console.log("✅ Generated timeline.svg successfully.");
    } catch (e) {
      console.error("❌ Error generating timeline.svg:", e);
    }
  } else {
    console.log("⏭️ Skipped timeline.svg generation (fast-run)");
  }

  // 6. GENERATE Heatmap SVG (Skip if fast)
  if (!isFastRun) {
    try {
      const heatmapPath = path.join(__dirname, '../readme-assets/heatmap.svg');
      const calendarData = await github.getContributionCalendar(owner);

      // Save heatmap cache
      saveCache("heatmap", { calendar: calendarData, timestamp: currentNow.toISOString() });

      const weeks = calendarData.weeks || [];
      const allDays = [];
      weeks.forEach(w => {
        if (w.contributionDays) {
          allDays.push(...w.contributionDays);
        }
      });

      let maxStreak = 0;
      let currStreak = 0;
      allDays.forEach(day => {
        const count = day.contributionCount || 0;
        if (count > 0) {
          currStreak++;
          if (currStreak > maxStreak) {
            maxStreak = currStreak;
          }
        } else {
          currStreak = 0;
        }
      });

      const daysOfWeek = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
      const weekdaySums = [0, 0, 0, 0, 0, 0, 0];
      allDays.forEach(day => {
        const weekday = day.weekday !== undefined ? day.weekday : new Date(day.date + 'T00:00:00Z').getUTCDay();
        weekdaySums[weekday] += (day.contributionCount || 0);
      });

      let busiestIdx = 2; // Default to TUE
      let maxSum = 0;
      const totalSum = weekdaySums.reduce((a, b) => a + b, 0);
      if (totalSum > 0) {
        for (let idx = 0; idx < 7; idx++) {
          if (weekdaySums[idx] > maxSum) {
            maxSum = weekdaySums[idx];
            busiestIdx = idx;
          }
        }
      }
      const busiestDay = daysOfWeek[busiestIdx];

      // Get peak hour from pre-calculated clockHours
      let maxCommits = Math.max(...clockHours);
      let peakHour = 21;
      if (maxCommits > 0) {
        peakHour = clockHours.indexOf(maxCommits);
      }
      const peakHourStr = `${String(peakHour).padStart(2, '0')}:00`;
      const busiestStr = `${busiestDay} ${peakHourStr}`;

      const heatmapElement = React.createElement(Heatmap, {
        weeks: calendarData.weeks || [],
        totalContributions: calendarData.totalContributions || 0,
        maxStreak: maxStreak,
        busiestStr: busiestStr
      });

      const heatmapSvg = await renderSvg(heatmapElement, 1100, 200);
      fs.writeFileSync(heatmapPath, heatmapSvg, 'utf8');
      console.log("✅ Generated heatmap.svg successfully.");
    } catch (e) {
      console.error("❌ Error generating heatmap.svg:", e);
    }
  } else {
    console.log("⏭️ Skipped heatmap.svg generation (fast-run)");
  }

  // 7. GENERATE Clock SVG (Skip if fast)
  if (!isFastRun) {
    try {
      const clockPath = path.join(__dirname, '../readme-assets/clock.svg');

      const maxCommits = Math.max(...clockHours);
      const peakHour = maxCommits > 0 ? clockHours.indexOf(maxCommits) : 0;
      const peakHourStr = `${String(peakHour).padStart(2, '0')}:00`;
      const peakPercent = totalClockCommits > 0 ? Math.round((clockHours[peakHour] / totalClockCommits) * 100) : 0;

      // Calculate productive window (3-hour max window)
      let maxWindowSum = -1;
      let bestStart = 0;
      for (let h = 0; h < 24; h++) {
        const wSum = clockHours[h] + clockHours[(h + 1) % 24] + clockHours[(h + 2) % 24];
        if (wSum > maxWindowSum) {
          maxWindowSum = wSum;
          bestStart = h;
        }
      }
      const prodWindowStr = `${String(bestStart).padStart(2, '0')}:00 – ${String((bestStart + 2) % 24).padStart(2, '0')}:00`;

      // Calculate quietest window (3-hour min window)
      let minWindowSum = 999999;
      let bestQuietStart = 0;
      for (let h = 0; h < 24; h++) {
        const wSum = clockHours[h] + clockHours[(h + 1) % 24] + clockHours[(h + 2) % 24];
        if (wSum < minWindowSum) {
          minWindowSum = wSum;
          bestQuietStart = h;
        }
      }
      const quietWindowStr = `${String(bestQuietStart).padStart(2, '0')}–${String((bestQuietStart + 2) % 24).padStart(2, '0')}`;
      const quietHoursStr = `${String(bestQuietStart).padStart(2, '0')} · ${String((bestQuietStart + 1) % 24).padStart(2, '0')} · ${String((bestQuietStart + 2) % 24).padStart(2, '0')}`;

      // Determine tag lines
      let tagLines = [];
      if (peakHour >= 22 || peakHour < 5) {
        tagLines = ['"Night-shift operator.', 'The frontier is quieter after dark."'];
      } else if (peakHour >= 5 && peakHour < 12) {
        tagLines = ['"Morning builder.', 'Securing the foundation at sunrise."'];
      } else if (peakHour >= 12 && peakHour < 17) {
        tagLines = ['"Afternoon focus.', 'Deep work under the high sun."'];
      } else {
        tagLines = ['"Evening observer.', 'Transmitting signals as twilight falls."'];
      }

      // Generate radial bars
      const paths = [];
      for (let h = 0; h < 24; h++) {
        const theta = h * (2 * Math.PI / 24) - (Math.PI / 2);
        const r1 = 55.0;
        let r2 = r1 + 1.0;
        if (maxCommits > 0) {
          r2 = r1 + (clockHours[h] / maxCommits) * 55.0;
        }
        const x1 = r1 * Math.cos(theta);
        const y1 = r1 * Math.sin(theta);
        const x2 = r2 * Math.cos(theta);
        const y2 = r2 * Math.sin(theta);
        
        let strokeColor;
        if (clockHours[h] === 0) {
          strokeColor = "#2a1f0c";
        } else if (h === peakHour) {
          strokeColor = GOLD_BRIGHT;
        } else if (clockHours[h] >= maxCommits * 0.5) {
          strokeColor = GOLD;
        } else {
          strokeColor = GOLD_DEEP;
        }
        
        paths.push(`      <path d="M ${x1.toFixed(1)} ${y1.toFixed(1)} L ${x2.toFixed(1)} ${y2.toFixed(1)}" stroke="${strokeColor}" stroke-width="6"></path>`);
      }
      const pathsJoined = paths.join('\n');

      const clockSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 380" width="720" height="380">
  <rect width="720" height="380" fill="${BG}"></rect>
  ${generateStars(720, 380, 15, 15)}

  <!-- Title -->
  <g font-family="${FONT_MONO}" font-size="11" fill="${GOLD}" letter-spacing="3">
    <text x="36" y="36">§ 04  ·  COMMIT  CLOCK  ·  24H  UTC</text>
    <text x="684" y="36" text-anchor="end" fill="${INK_DIM}">LAST 90 DAYS · ${totalClockCommits} COMMITS</text>
  </g>

  <!-- Clock Center -->
  <g transform="translate(170 210)">
    <circle r="120" fill="none" stroke="${BG_PANEL}"></circle>
    <circle r="55" fill="none" stroke="${BG_PANEL}"></circle>

    <!-- Clock Ticks -->
    <g stroke="${GOLD}" stroke-width="1" opacity="0.6">
      <line x1="0" y1="-126" x2="0" y2="-134"></line>
      <line x1="126" y1="0" x2="134" y2="0"></line>
      <line x1="0" y1="126" x2="0" y2="134"></line>
      <line x1="-126" y1="0" x2="-134" y2="0"></line>
    </g>
    <g font-family="${FONT_MONO}" font-size="10" fill="${INK_MID}" letter-spacing="2" text-anchor="middle">
      <text x="0" y="-142">00</text>
      <text x="148" y="4">06</text>
      <text x="0" y="156">12</text>
      <text x="-148" y="4">18</text>
    </g>

    <!-- Radial Bars -->
    <g stroke="${INK_DIM}" stroke-width="0.5">
${pathsJoined}
    </g>

    <!-- Center Ring -->
    <circle r="38" fill="${BG}" stroke="${GOLD}"></circle>
    <text y="-4" text-anchor="middle" font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}" font-weight="500">${peakHourStr}</text>
    <text y="14" text-anchor="middle" font-family="${FONT_MONO}" font-size="8" fill="${INK_DIM}" letter-spacing="3">PEAK · UTC</text>
  </g>

  <!-- Right Details -->
  <g transform="translate(380 110)" font-family="${FONT_MONO}" fill="${INK_MID}" font-size="10" letter-spacing="2">
    <g>
      <text fill="${INK_DIM}">PRODUCTIVE WINDOW</text>
      <text y="22" font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}" font-weight="500">${prodWindowStr}<tspan fill="${GOLD}" font-size="11" font-family="${FONT_MONO}" letter-spacing="2">  UTC</tspan></text>
    </g>
    <g transform="translate(0 60)">
      <text fill="${INK_DIM}">PEAK HOUR · ${peakHourStr}</text>
      <text y="22" font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}" font-weight="500">${peakPercent}<tspan font-size="14" fill="${INK_MID}">% of all commits</tspan></text>
    </g>
    <g transform="translate(0 120)">
      <text fill="${INK_DIM}">QUIETEST · ${quietWindowStr}</text>
      <text y="22" font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}" font-weight="500">${quietHoursStr}</text>
    </g>
    <g transform="translate(0 190)">
      <line x1="0" y1="-4" x2="280" y2="-4" stroke="${BG_PANEL}" stroke-dasharray="2 3"></line>
      <text y="14" font-family="${FONT_SERIF}" font-size="14" fill="${INK}" font-style="italic">${tagLines[0]}</text>
      <text y="34" font-family="${FONT_SERIF}" font-size="14" fill="${INK}" font-style="italic">${tagLines[1]}</text>
    </g>
  </g>
</svg>`;

      fs.writeFileSync(clockPath, clockSvg, 'utf8');
      console.log("✅ Generated clock.svg successfully.");
    } catch (e) {
      console.error("❌ Error generating clock.svg:", e);
    }
  } else {
    console.log("⏭️ Skipped clock.svg generation (fast-run)");
  }

  // 8. UPDATE README.md sections
  const readmePath = path.join(__dirname, '../README.md');
  if (fs.existsSync(readmePath)) {
    let readmeText = fs.readFileSync(readmePath, 'utf8');

    // Section A: TELEMETRY
    try {
      let commits_30d = 184;
      let merged_prs = 23;
      let closed_issues = 41;
      let active_repos = 6;
      let total_stars = 1300;
      let sparkline = "✓✓✓✓✗✓✓✓✓✓";
      let rate_remaining = 4870;
      let rate_limit = 5000;

      try {
        const metrics = await github.getActivityMetrics(owner, 30);
        const repos = await github.getRepos(owner);
        const wf = await github.getWorkflowHealth(owner, 'deepextrema');
        const rate = await github.getRateLimit();

        commits_30d = metrics.commits_count !== undefined ? metrics.commits_count : 184;
        merged_prs = metrics.merged_prs_count !== undefined ? metrics.merged_prs_count : 23;
        closed_issues = metrics.closed_issues_count !== undefined ? metrics.closed_issues_count : 41;
        active_repos = metrics.active_repos_count !== undefined ? metrics.active_repos_count : 6;
        total_stars = repos.length > 0 ? repos.reduce((acc, r) => acc + (r.stargazers_count || 0), 0) : 1300;
        sparkline = wf.sparkline || "✅✅✅✅❌✅✅✅❌✅";
        rate_remaining = rate.remaining !== undefined ? rate.remaining : 4870;
        rate_limit = rate.limit !== undefined ? rate.limit : 5000;
      } catch (err) {
        console.warn("Using fallback telemetry data due to error:", err.message);
      }

      const stars_str = formatNumber(total_stars);
      const telemetryBody = `<sub align="center">
<b>TELEMETRY ·</b>
COMMITS·30D <code>${commits_30d}</code>  ·
PR·MERGED <code>${merged_prs}</code>  ·
ISSUES·CLOSED <code>${closed_issues}</code>  ·
ACTIVE·REPOS <code>${active_repos}</code>  ·
STARS·TOTAL <code>${stars_str}</code>  ·
WORKFLOWS <code>${sparkline}</code>  ·
RATE·LIMIT <code>${rate_remaining}/${rate_limit}</code>
</sub>`;
      
      readmeText = injectMarkdown(readmeText, "TELEMETRY", telemetryBody);
      console.log("✅ Injected TELEMETRY section in README.");
    } catch (e) {
      console.error("Error updating TELEMETRY section:", e);
    }

    // Section B: SIGNAL_FEED
    try {
      const space = await getSpaceSignal();
      const ai = await getAiSignal();
      const phrase = await getPhraseSignal();

      // Save cache of successful fetches
      const cacheToSave = { timestamp: currentNow.toISOString() };
      if (!space.stale) {
        cacheToSave.space = space;
      } else {
        const oldCache = loadCache("signal_feed");
        if (oldCache && oldCache.space) {
          cacheToSave.space = oldCache.space;
        }
      }
      if (!ai.stale) {
        cacheToSave.ai = ai;
      } else {
        const oldCache = loadCache("signal_feed");
        if (oldCache && oldCache.ai) {
          cacheToSave.ai = oldCache.ai;
        }
      }
      saveCache("signal_feed", cacheToSave);

      const spaceStale = space.stale ? " (stale)" : "";
      const aiStale = ai.stale ? " (stale)" : "";

      const signalFeedBody = `<table>
<tr>
<td width="33%" align="center" valign="top">

**🜨 SPACE**${spaceStale}

${space.title || 'Signal'} — ${truncateString(space.description || '', 80)}

<sub>NASA APOD · ${space.date || ''}</sub>

</td>
<td width="33%" align="center" valign="top">

**◇ AI**${aiStale}

[${ai.name || 'Model'}](${ai.url || '#'})

<sub>HF TRENDING · ${(ai.description || 'MODEL').toUpperCase()}</sub>

</td>
<td width="33%" align="center" valign="top">

**✺ PHRASE**

> *${phrase.text || 'Loading...'}*

<sub>${(phrase.source || 'GENERATED').toUpperCase()} · DAILY</sub>

</td>
</tr>
</table>`;

      readmeText = injectMarkdown(readmeText, "SIGNAL_FEED", signalFeedBody);
      console.log("✅ Injected SIGNAL_FEED section in README.");
    } catch (e) {
      console.error("Error updating SIGNAL_FEED section:", e);
    }

    // Section C: FOOTER
    try {
      let commitHash = "a3f12b9";
      try {
        const { execSync } = require('child_process');
        commitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim();
      } catch (err) {
        // use fallback
      }

      const year = currentNow.getUTCFullYear();
      const month = String(currentNow.getUTCMonth() + 1).padStart(2, '0');
      const day = String(currentNow.getUTCDate()).padStart(2, '0');
      const hours = String(currentNow.getUTCHours()).padStart(2, '0');
      const minutes = String(currentNow.getUTCMinutes()).padStart(2, '0');
      const lastBuildStr = `${year}-${month}-${day} ${hours}:${minutes} UTC`;

      const footerBody = `<div align="center">

<sub>
LAST BUILD <code>${lastBuildStr}</code>  ·  NEXT SYNC <code>+6h</code>  ·  WORKFLOW <code>update-cockpit.yml ✓</code>  ·  COMMIT <code>${commitHash}</code>
</sub>

</div>`;

      readmeText = injectMarkdown(readmeText, "FOOTER", footerBody);
      console.log("✅ Injected FOOTER section in README.");
    } catch (e) {
      console.error("Error updating FOOTER section:", e);
    }

    // Write back the final README.md file
    fs.writeFileSync(readmePath, readmeText, 'utf8');
    console.log("🎉 Successfully wrote updated README.md!");
  } else {
    console.warn(`⚠️ README.md not found at ${readmePath}`);
  }
}

// Exports for tests and CLI execution
module.exports = {
  injectMarkdown,
  main
};

if (require.main === module) {
  main().catch(err => {
    console.error("Fatal error running pipeline:", err);
    process.exit(1);
  });
}
