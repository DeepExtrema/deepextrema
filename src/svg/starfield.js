function seeded(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

function starfield(width, height, count = 12, seed = 1) {
  const rnd = seeded(seed);
  const stars = [];
  for (let i = 0; i < count; i++) {
    const x = Math.round(rnd() * width);
    const y = Math.round(rnd() * height);
    const r = (0.5 + rnd() * 0.6).toFixed(2);
    const op = (0.4 + rnd() * 0.4).toFixed(2);
    stars.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="#f5e6b8" opacity="${op}"/>`);
  }
  return `<g>${stars.join('')}</g>`;
}

module.exports = { starfield };
