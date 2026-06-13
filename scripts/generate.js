require('dotenv').config();
const fs = require('fs');
const path = require('path');

const { loadConfig } = require('../src/config');
const { renderHero } = require('../src/svg/hero');
const { renderAbout } = require('../src/svg/about');
const { renderProjectTile } = require('../src/svg/projectTile');
const { renderButton } = require('../src/svg/contactButton');
const { renderFooter } = require('../src/svg/footer');
const { renderHeatmap } = require('../src/svg/heatmap');
const { renderSectionHeader } = require('../src/svg/sectionHeader');
const { fetchContributionWeeks } = require('../src/data/contributions');
const { sampleHistoryWeeks } = require('../src/data/sampleHistory');

const TILE_FILES = ['work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg'];

const DEFAULT_SECTIONS = {
  work: { num: '02', title: 'Selected work', subtitle: 'Projects worth tracking' },
  historyLive: { num: '03', title: 'Transmission record', subtitle: 'Live GitHub calendar' },
  historyExample: { num: '04', title: 'Arbitrary history', subtitle: 'Synthetic { date, count } demo' },
  contact: { num: '05', title: 'Contact', subtitle: null },
};

function write(outDir, file, svg) {
  fs.writeFileSync(path.join(outDir, file), svg, 'utf8');
}

function section(cfg, key) {
  return (cfg.sections && cfg.sections[key]) || DEFAULT_SECTIONS[key];
}

async function generate({ cfg, outDir, token, fetchWeeks }) {
  fs.mkdirSync(outDir, { recursive: true });

  write(outDir, 'hero.svg', renderHero(cfg));
  write(outDir, 'about.svg', renderAbout(cfg));

  write(outDir, 'section-work.svg', renderSectionHeader(section(cfg, 'work')));
  cfg.projects.forEach((p, i) => write(outDir, TILE_FILES[i], renderProjectTile(p)));

  write(outDir, 'section-history-live.svg', renderSectionHeader(section(cfg, 'historyLive')));

  write(outDir, 'section-history-example.svg', renderSectionHeader(section(cfg, 'historyExample')));
  write(outDir, 'heatmap-example.svg', renderHeatmap(sampleHistoryWeeks(), {
    title: 'Signal archive',
    legend: '52 WEEKS · SYNTHETIC · ARBITRARY DATA',
  }));

  write(outDir, 'section-contact.svg', renderSectionHeader(section(cfg, 'contact')));
  cfg.links.forEach((l) => write(outDir, l.file, renderButton(l.label)));
  write(outDir, 'footer.svg', renderFooter(cfg));

  try {
    const weeks = await (fetchWeeks || fetchContributionWeeks)(cfg.githubLogin, token);
    write(outDir, 'heatmap.svg', renderHeatmap(weeks, {
      title: 'Transmission record',
      legend: `${weeks.length} WEEKS · LIVE · GITHUB`,
    }));
  } catch (e) {
    const existing = path.join(outDir, 'heatmap.svg');
    if (fs.existsSync(existing)) {
      console.warn(`Heatmap fetch failed (${e.message}); keeping existing heatmap.svg`);
    } else {
      console.warn(`Heatmap fetch failed (${e.message}); writing empty-state heatmap`);
      write(outDir, 'heatmap.svg', renderHeatmap([], { legend: 'NO SIGNAL · OFFLINE' }));
    }
  }
}

async function main() {
  const cfg = loadConfig();
  const outDir = path.join(__dirname, '..', 'assets');
  await generate({ cfg, outDir, token: process.env.GITHUB_TOKEN });
  console.log('✦ Generated README assets in assets/');
}

module.exports = { generate, main, TILE_FILES, DEFAULT_SECTIONS };

if (require.main === module) {
  main().catch((err) => { console.error(err); process.exit(1); });
}
