const fs = require('fs');
const os = require('os');
const path = require('path');
const { generate } = require('../scripts/generate');
const { loadConfig } = require('../src/config');

test('generate writes all box SVGs and preserves transmission record on fetch failure', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  fs.writeFileSync(path.join(out, 'transmission-record.svg'), '<svg>OLD</svg>');
  fs.writeFileSync(path.join(out, 'transmission-record.gif'), Buffer.from('GIF89aOLD'));
  const cfg = loadConfig();
  const failingFetch = async () => { throw new Error('network down'); };

  await generate({ cfg, outDir: out, token: 't', fetchWeeks: failingFetch });

  const expected = ['hero.svg', 'about.svg', 'footer.svg', 'transmission-record.svg', 'transmission-record.gif',
    'section-work.svg', 'section-history-live.svg', 'section-contact.svg',
    'work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg',
    'btn-github.svg', 'btn-website.svg', 'btn-parallax.svg'];
  expected.forEach((f) => expect(fs.existsSync(path.join(out, f))).toBe(true));
  expect(fs.readFileSync(path.join(out, 'transmission-record.svg'), 'utf8')).toBe('<svg>OLD</svg>');
  expect(fs.readFileSync(path.join(out, 'transmission-record.gif')).toString()).toBe('GIF89aOLD');
});

test('generate writes a fresh transmission record when fetch succeeds', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  const cfg = loadConfig();
  const okFetch = async () => ([[{ date: '2026-01-01', count: 3 }]]);
  await generate({ cfg, outDir: out, token: 't', fetchWeeks: okFetch });
  const svg = fs.readFileSync(path.join(out, 'transmission-record.svg'), 'utf8');
  expect(svg).toContain('<svg');
  expect(svg).toContain('SIGNAL TRAIL');
  expect(fs.existsSync(path.join(out, 'transmission-record.gif'))).toBe(true);
});
