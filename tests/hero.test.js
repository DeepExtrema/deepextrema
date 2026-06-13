const { renderHero } = require('../src/svg/hero');
const cfg = { name: 'DeepExtrema', tagline: 'Turning scattered signals into constellations' };

test('hero contains split name and tagline and a disc gradient', () => {
  const svg = renderHero(cfg);
  expect(svg.startsWith('<svg')).toBe(true);
  expect(svg).toContain('Deep');
  expect(svg).toContain('Extrema');
  expect(svg).toContain('Turning scattered signals into constellations');
  expect(svg).toContain('radialGradient');     // glow via gradients, not filters
  expect(svg).not.toContain('feGaussianBlur');  // no fragile filters
});
