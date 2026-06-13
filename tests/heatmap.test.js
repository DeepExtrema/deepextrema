const { renderHeatmap, levelOf } = require('../src/svg/heatmap');

test('levelOf buckets counts 0..5', () => {
  expect(levelOf(0)).toBe(0);
  expect(levelOf(1)).toBe(1);
  expect(levelOf(100)).toBe(5);
});

test('heatmap renders one rect per day plus a label', () => {
  const weeks = [
    [{ date: '2026-01-01', count: 0 }, { date: '2026-01-02', count: 2 }],
    [{ date: '2026-01-03', count: 9 }],
  ];
  const svg = renderHeatmap(weeks);
  expect(svg.startsWith('<svg')).toBe(true);
  expect((svg.match(/<rect/g) || []).length).toBeGreaterThanOrEqual(3 + 1); // 3 days + frame rect
  expect(svg).toContain('TRANSMISSION RECORD');
});
