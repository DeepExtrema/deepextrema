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
const { fetchContributionWeeks } = require('../src/data/contributions');

const TILE_FILES = ['work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg'];

function write(outDir, file, svg) {
  fs.writeFileSync(path.join(outDir, file), svg, 'utf8');
}

async function generate({ cfg, outDir, token, fetchWeeks }) {
  fs.mkdirSync(outDir, { recursive: true });

  write(outDir, 'hero.svg', renderHero(cfg));
  write(outDir, 'about.svg', renderAbout(cfg));
  cfg.projects.forEach((p, i) => write(outDir, TILE_FILES[i], renderProjectTile(p)));
  cfg.links.forEach((l) => write(outDir, l.file, renderButton(l.label)));
  write(outDir, 'footer.svg', renderFooter(cfg));

  // heatmap: only piece that can fail; never overwrite a good file with broken output
  try {
    const weeks = await (fetchWeeks || fetchContributionWeeks)(cfg.githubLogin, token);
    write(outDir, 'heatmap.svg', renderHeatmap(weeks));
  } catch (e) {
    const existing = path.join(outDir, 'heatmap.svg');
    if (fs.existsSync(existing)) {
      console.warn(`Heatmap fetch failed (${e.message}); keeping existing heatmap.svg`);
    } else {
      console.warn(`Heatmap fetch failed (${e.message}); writing empty-state heatmap`);
      write(outDir, 'heatmap.svg', renderHeatmap([]));
    }
  }
}

async function main() {
  const cfg = loadConfig();
  const outDir = path.join(__dirname, '..', 'assets');
  await generate({ cfg, outDir, token: process.env.GITHUB_TOKEN });
  console.log('✦ Generated README assets in assets/');
}

module.exports = { generate, main, TILE_FILES };

if (require.main === module) {
  main().catch((err) => { console.error(err); process.exit(1); });
}
