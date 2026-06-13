const fs = require('fs');
const os = require('os');
const path = require('path');
const { renderTransmissionGif, FRAME_COUNT } = require('../src/animation/transmissionGif');

test('renderTransmissionGif produces a looping GIF under 2MB', () => {
  const weeks = [];
  for (let w = 0; w < 52; w += 1) {
    const days = [];
    for (let d = 0; d < 7; d += 1) {
      days.push({ date: `2026-W${w}-D${d}`, count: (w + d) % 4 === 0 ? 3 : 0 });
    }
    weeks.push(days);
  }

  const gif = renderTransmissionGif(weeks, { legend: '52 WEEKS · TEST' });
  expect(Buffer.isBuffer(gif)).toBe(true);
  expect(gif.slice(0, 3).toString()).toBe('GIF');
  expect(gif.length).toBeLessThan(2 * 1024 * 1024);
});

test('renderTransmissionGif uses expected frame count', () => {
  expect(FRAME_COUNT).toBe(60);
});
