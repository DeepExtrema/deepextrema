require('dotenv').config();
const fs = require('fs');
const path = require('path');

const { loadConfig } = require('../src/config');
const { renderColophon } = require('../src/svg/colophon');
const { fetchContributionWeeks } = require('../src/data/contributions');

const FILES = { light: 'colophon-light.svg', dark: 'colophon-dark.svg' };

function write(outDir, file, svg) {
  fs.writeFileSync(path.join(outDir, file), svg, 'utf8');
}

async function generate({ cfg, outDir, token, fetchWeeks }) {
  fs.mkdirSync(outDir, { recursive: true });

  let weeks = [];
  try {
    weeks = await (fetchWeeks || fetchContributionWeeks)(cfg.githubLogin, token);
  } catch (e) {
    const existing = Object.values(FILES).every((f) => fs.existsSync(path.join(outDir, f)));
    if (existing) {
      console.warn(`Contribution fetch failed (${e.message}); keeping existing plates`);
      return;
    }
    console.warn(`Contribution fetch failed (${e.message}); rendering without activity data`);
  }

  write(outDir, FILES.light, renderColophon(cfg, weeks, { theme: 'light' }));
  write(outDir, FILES.dark, renderColophon(cfg, weeks, { theme: 'dark' }));
}

async function main() {
  const cfg = loadConfig();
  const outDir = path.join(__dirname, '..', 'assets');
  await generate({ cfg, outDir, token: process.env.GITHUB_TOKEN });
  console.log('Generated README plates in assets/');
}

module.exports = { generate, main, FILES };

if (require.main === module) {
  main().catch((err) => { console.error(err); process.exit(1); });
}
