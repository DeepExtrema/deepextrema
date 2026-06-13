const fs = require('fs');
const os = require('os');
const path = require('path');
const { generate } = require('../scripts/generate');
const { loadConfig } = require('../src/config');

test('generate writes all box SVGs and preserves heatmap on fetch failure', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  // seed an existing heatmap to prove fallback preserves it
  fs.writeFileSync(path.join(out, 'heatmap.svg'), '<svg>OLD</svg>');
  const cfg = loadConfig();
  const failingFetch = async () => { throw new Error('network down'); };

  await generate({ cfg, outDir: out, token: 't', fetchWeeks: failingFetch });

  const expected = ['hero.svg', 'about.svg', 'footer.svg',
    'section-work.svg', 'section-history-live.svg', 'section-history-example.svg', 'section-contact.svg',
    'heatmap-example.svg',
    'work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg',
    'btn-github.svg', 'btn-website.svg', 'btn-parallax.svg'];
  expected.forEach((f) => expect(fs.existsSync(path.join(out, f))).toBe(true));
  // heatmap untouched because fetch failed and a file existed
  expect(fs.readFileSync(path.join(out, 'heatmap.svg'), 'utf8')).toBe('<svg>OLD</svg>');
});

test('generate writes a fresh heatmap when fetch succeeds', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  const cfg = loadConfig();
  const okFetch = async () => ([[{ date: '2026-01-01', count: 3 }]]);
  await generate({ cfg, outDir: out, token: 't', fetchWeeks: okFetch });
  expect(fs.readFileSync(path.join(out, 'heatmap.svg'), 'utf8')).toContain('<svg');
});
