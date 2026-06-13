const { buildTrailPath, gridLayout } = require('../src/data/trailPath');

test('buildTrailPath returns chronological points only for days with activity', () => {
  const weeks = [
    [{ date: '2026-01-01', count: 0 }, { date: '2026-01-02', count: 3 }],
    [{ date: '2026-01-03', count: 0 }, { date: '2026-01-04', count: 1 }],
  ];
  const { points } = buildTrailPath(weeks);
  expect(points).toHaveLength(2);
  expect(points[0].date).toBe('2026-01-02');
  expect(points[1].date).toBe('2026-01-04');
});

test('gridLayout centers a 52-week grid in 840px width', () => {
  const { startX, cell, padTop } = gridLayout(52);
  expect(startX).toBeGreaterThan(0);
  expect(cell).toBe(11);
  expect(padTop).toBe(64);
});

test('buildTrailPath assigns cell center coordinates', () => {
  const weeks = [[{ date: '2026-01-01', count: 5 }]];
  const { points } = buildTrailPath(weeks);
  expect(points[0].x).toBeGreaterThan(0);
  expect(points[0].y).toBeGreaterThan(0);
});
