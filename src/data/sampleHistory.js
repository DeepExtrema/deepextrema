function seeded(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

function isoDate(base, offsetDays) {
  const d = new Date(base);
  d.setUTCDate(d.getUTCDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

/** Build a deterministic 52-week history from arbitrary intensity phases (no GitHub API). */
function sampleHistoryWeeks(weekCount = 52, seed = 11) {
  const rnd = seeded(seed);
  const base = Date.UTC(2025, 5, 15);
  const weeks = [];

  for (let w = 0; w < weekCount; w++) {
    let phase = 0;
    if (w >= 8 && w < 22) phase = 14;
    else if (w >= 28 && w < 36) phase = 7;
    else if (w % 11 === 0) phase = 5;

    const days = [];
    for (let d = 0; d < 7; d++) {
      const jitter = Math.floor(rnd() * 10) - 3;
      const count = Math.max(0, Math.floor(phase * (0.35 + rnd() * 0.65) + jitter));
      days.push({ date: isoDate(base, w * 7 + d), count });
    }
    weeks.push(days);
  }

  return weeks;
}

module.exports = { sampleHistoryWeeks, seeded };
