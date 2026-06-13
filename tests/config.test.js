const path = require('path');
const { loadConfig } = require('../src/config');

test('loads the real profile.config.json with required fields', () => {
  const cfg = loadConfig();
  expect(cfg.name).toBe('DeepExtrema');
  expect(cfg.tagline).toMatch(/constellations/);
  expect(cfg.projects).toHaveLength(4);
  expect(cfg.links.length).toBeGreaterThanOrEqual(2);
});

test('throws when a required field is missing', () => {
  const bad = path.join(__dirname, 'fixtures', 'bad.config.json');
  expect(() => loadConfig(bad)).toThrow(/missing required/i);
});
