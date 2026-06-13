require('dotenv').config();
const fs = require('fs');
const path = require('path');

const { loadConfig } = require('../src/config');
const { renderHero } = require('../src/svg/hero');
const { renderAbout } = require('../src/svg/about');
const { renderProjectTile } = require('../src/svg/projectTile');
const { renderButton } = require('../src/svg/contactButton');
const { renderFooter } = require('../src/svg/footer');
const { renderTransmissionTrail } = require('../src/svg/transmissionTrail');
const { renderTransmissionGif } = require('../src/animation/transmissionGif');
const { renderSectionHeader } = require('../src/svg/sectionHeader');
const { fetchContributionWeeks } = require('../src/data/contributions');

const TILE_FILES = ['work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg'];

const DEFAULT_SECTIONS = {
  work: { num: '02', title: 'Selected work', subtitle: 'Four projects — each tile links through to the repo' },
  historyLive: { num: '03', title: 'Transmission record', subtitle: 'Live signal trail from GitHub — refreshed daily' },
  contact: { num: '04', title: 'Contact', subtitle: 'Open channels' },
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

  write(outDir, 'section-contact.svg', renderSectionHeader(section(cfg, 'contact')));
  cfg.links.forEach((l) => write(outDir, l.file, renderButton(l.label)));
  write(outDir, 'footer.svg', renderFooter(cfg));

  const recordSvgPath = path.join(outDir, 'transmission-record.svg');
  const recordGifPath = path.join(outDir, 'transmission-record.gif');
  try {
    const weeks = await (fetchWeeks || fetchContributionWeeks)(cfg.githubLogin, token);
    const trailOpts = {
      legend: `${weeks.length} WEEKS · LIVE · GITHUB · SIGNAL TRAIL`,
    };
    write(outDir, 'transmission-record.svg', renderTransmissionTrail(weeks, trailOpts));
    try {
      fs.writeFileSync(recordGifPath, renderTransmissionGif(weeks, trailOpts));
    } catch (gifErr) {
      if (fs.existsSync(recordGifPath)) {
        console.warn(`GIF generation failed (${gifErr.message}); keeping existing transmission-record.gif`);
      } else {
        console.warn(`GIF generation failed (${gifErr.message}); README will fall back to static SVG`);
      }
    }
  } catch (e) {
    if (fs.existsSync(recordSvgPath)) {
      console.warn(`Transmission fetch failed (${e.message}); keeping existing transmission-record.svg`);
    } else {
      console.warn(`Transmission fetch failed (${e.message}); writing offline transmission record`);
      write(outDir, 'transmission-record.svg', renderTransmissionTrail([]));
    }
    if (fs.existsSync(recordGifPath)) {
      console.warn(`Transmission fetch failed (${e.message}); keeping existing transmission-record.gif`);
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
