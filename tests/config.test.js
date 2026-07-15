const path = require('path');
const { loadConfig } = require('../src/config');

test('loads the real profile.config.json with required fields', () => {
  const cfg = loadConfig();
  expect(cfg.name).toBe('Taimoor Awan');
  expect(cfg.githubLogin).toBe('DeepExtrema');
  expect(cfg.now.name).toBe('Ephemeris');
  expect(cfg.now.lines.length).toBeGreaterThanOrEqual(1);
  expect(cfg.projects).toHaveLength(4);
  cfg.projects.forEach((p) => {
    expect(p.url).toMatch(/^https:\/\/github\.com\/DeepExtrema\//);
    expect(p.language).toBeTruthy();
    expect(p.year).toMatch(/^\d{4}$/);
  });
  expect(cfg.colophon.addresses.length).toBeGreaterThanOrEqual(2);
});

test('throws when a required field is missing', () => {
  const bad = path.join(__dirname, 'fixtures', 'bad.config.json');
  expect(() => loadConfig(bad)).toThrow(/missing required/i);
});

test('throws when a project entry is incomplete', () => {
  const bad = path.join(__dirname, 'fixtures', 'bad.project.config.json');
  expect(() => loadConfig(bad)).toThrow(/projects\[0\]\.language/);
});
