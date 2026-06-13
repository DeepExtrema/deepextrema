const { renderTransmissionTrail } = require('../src/svg/transmissionTrail');

test('transmission trail includes probe, dashed path, and legend', () => {
  const weeks = [
    [{ date: '2026-01-01', count: 2 }, { date: '2026-01-02', count: 0 }],
    [{ date: '2026-01-03', count: 5 }],
  ];
  const svg = renderTransmissionTrail(weeks, { legend: '2 WEEKS · TEST' });
  expect(svg.startsWith('<svg')).toBe(true);
  expect(svg).toContain('TRANSMISSION RECORD');
  expect(svg).toContain('stroke-dasharray');
  expect(svg).toContain('2 WEEKS · TEST');
  expect(svg).not.toContain('NaN');
});

test('empty weeks renders offline state without probe path', () => {
  const svg = renderTransmissionTrail([]);
  expect(svg).toContain('NO SIGNAL');
});
