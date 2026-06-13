const { starfield } = require('../src/svg/starfield');

test('starfield is deterministic for a given seed and count', () => {
  const a = starfield(800, 280, 12, 7);
  const b = starfield(800, 280, 12, 7);
  expect(a).toBe(b);
  expect((a.match(/<circle/g) || []).length).toBe(12);
});
