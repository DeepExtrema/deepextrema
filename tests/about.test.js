const { renderAbout, wrap } = require('../src/svg/about');

test('wrap breaks text into lines under the max char width', () => {
  const lines = wrap('one two three four five six', 12);
  expect(lines.length).toBeGreaterThan(1);
  lines.forEach((l) => expect(l.length).toBeLessThanOrEqual(13));
});

test('about contains lede, body and currently text', () => {
  const cfg = {
    about: { lede: 'Hard problems only.', body: 'Founder and engineer chasing faint signals across the edge.' },
    currently: { text: 'Currently building Ephemeris', url: 'https://example.com' },
  };
  const svg = renderAbout(cfg);
  expect(svg).toContain('Hard problems only.');
  expect(svg).toContain('Founder and engineer');
  expect(svg).toContain('Currently building Ephemeris');
  expect(svg).not.toContain('NaN'); // guard against swapped lineH/attrs coordinates
});
