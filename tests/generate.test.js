const fs = require('fs');
const os = require('os');
const path = require('path');
const { generate, FILES } = require('../scripts/generate');
const { loadConfig } = require('../src/config');

const okWeeks = [
  [{ date: '2026-06-29', count: 3 }, { date: '2026-06-30', count: 1 }],
  [{ date: '2026-07-06', count: 2 }],
];

test('generate writes light and dark plates when the fetch succeeds', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  await generate({ cfg: loadConfig(), outDir: out, token: 't', fetchWeeks: async () => okWeeks });
  for (const f of Object.values(FILES)) {
    const svg = fs.readFileSync(path.join(out, f), 'utf8');
    expect(svg).toContain('<svg');
    expect(svg).toContain('TAIMOOR AWAN');
    expect(svg).toContain('6 TOTAL');
  }
});

test('generate keeps existing plates when the fetch fails', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  fs.writeFileSync(path.join(out, FILES.light), '<svg>OLD-LIGHT</svg>');
  fs.writeFileSync(path.join(out, FILES.dark), '<svg>OLD-DARK</svg>');
  await generate({ cfg: loadConfig(), outDir: out, token: 't', fetchWeeks: async () => { throw new Error('down'); } });
  expect(fs.readFileSync(path.join(out, FILES.light), 'utf8')).toBe('<svg>OLD-LIGHT</svg>');
  expect(fs.readFileSync(path.join(out, FILES.dark), 'utf8')).toBe('<svg>OLD-DARK</svg>');
});

test('generate renders the offline fallback when the fetch fails and no plates exist', async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'assets-'));
  await generate({ cfg: loadConfig(), outDir: out, token: 't', fetchWeeks: async () => { throw new Error('down'); } });
  const svg = fs.readFileSync(path.join(out, FILES.light), 'utf8');
  expect(svg).toContain('No activity data yet.');
});
