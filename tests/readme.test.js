const fs = require('fs');
const path = require('path');
const { loadConfig } = require('../src/config');

const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');

test('README serves the plate with a dark-scheme source', () => {
  expect(readme).toContain('<picture>');
  expect(readme).toContain('media="(prefers-color-scheme: dark)"');
  expect(readme).toContain('srcset="assets/colophon-dark.svg"');
  expect(readme).toContain('src="assets/colophon-light.svg"');
  expect(readme).toMatch(/alt="[^"]{100,}"/);
});

test('README links every project plus the site links', () => {
  const cfg = loadConfig();
  cfg.projects.forEach((p) => expect(readme).toContain(`href="${p.url}"`));
  cfg.links.forEach((l) => expect(readme).toContain(`href="${l.url}"`));
});

test('README carries no leftovers from the previous design', () => {
  ['hero.svg', 'transmission-record', 'btn-github', 'constellation', 'SIGNAL OUTBOUND'].forEach((s) => {
    expect(readme).not.toContain(s);
  });
});
