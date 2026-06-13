const { sampleHistoryWeeks } = require('../src/data/sampleHistory');

test('sampleHistoryWeeks returns deterministic 52-week matrices', () => {
  const a = sampleHistoryWeeks(52, 11);
  const b = sampleHistoryWeeks(52, 11);
  expect(a).toEqual(b);
  expect(a).toHaveLength(52);
  expect(a[0]).toHaveLength(7);
  expect(a[0][0]).toMatchObject({ date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/), count: expect.any(Number) });
});

test('sampleHistoryWeeks accepts custom week counts', () => {
  expect(sampleHistoryWeeks(12, 7)).toHaveLength(12);
});
