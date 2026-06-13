const { box, escapeXml } = require('./frame');
const { buildTrailPath, CELL, SIZE, PAD_TOP, W } = require('../data/trailPath');

const DIM = '#0a0805';
const LEVELS = ['#1a1308', '#5a4220', '#7d5d2a', '#a37a3a', '#d4a85a'];
const H = PAD_TOP + 7 * CELL + 40;

function levelOf(count) {
  if (count <= 0) return 0;
  if (count < 2) return 1;
  if (count < 5) return 2;
  if (count < 10) return 3;
  return 4;
}

function renderProbe(x, y) {
  return `
  <circle cx="${x}" cy="${y}" r="14" fill="#d4a85a" opacity="0.12"/>
  <g transform="translate(${x} ${y})" fill="none" stroke="#f5e6b8" stroke-width="1.1">
    <circle r="6" stroke-width="1.2" fill="#1a1308"/>
    <line x1="0" y1="-6" x2="0" y2="-16"/>
    <line x1="-6" y1="0" x2="-18" y2="4"/>
    <line x1="6" y1="0" x2="18" y2="4"/>
    <circle r="1.5" fill="#f5e6b8" stroke="none"/>
  </g>`;
}

function visitIndex(points, progress) {
  if (points.length === 0) return -1;
  if (progress >= 1) return points.length - 1;
  return Math.min(points.length - 1, Math.floor(progress * points.length));
}

function renderTransmissionTrail(weeks, opts = {}) {
  const {
    title = 'Transmission record',
    legend,
    progress,
    embedFonts = true,
    fontsDir,
  } = opts;
  const animated = progress !== undefined;
  const { points, layout } = buildTrailPath(weeks);
  const cols = weeks.length || 52;
  const startX = layout.startX;
  const idx = animated ? visitIndex(points, progress) : points.length - 1;

  const visited = new Set();
  if (idx >= 0) {
    for (let i = 0; i <= idx; i += 1) {
      visited.add(`${points[i].week},${points[i].day}`);
    }
  }

  let grid = '';
  for (let wi = 0; wi < cols; wi++) {
    for (let di = 0; di < 7; di++) {
      const x = startX + wi * CELL;
      const y = PAD_TOP + di * CELL;
      const day = weeks[wi]?.[di];
      const count = day?.count ?? 0;
      const onTrail = animated
        ? visited.has(`${wi},${di}`)
        : points.some((p) => p.week === wi && p.day === di);
      const fill = onTrail ? LEVELS[levelOf(count)] : DIM;
      const opacity = onTrail ? 0.95 : 0.55;
      grid += `<rect x="${x}" y="${y}" width="${SIZE}" height="${SIZE}" rx="2" fill="${fill}" opacity="${opacity}"/>`;
    }
  }

  let trail = '';
  const trailPoints = idx >= 0 ? points.slice(0, idx + 1) : [];
  if (trailPoints.length > 1) {
    const d = trailPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
    trail = `<path d="${d}" fill="none" stroke="#d4a85a" stroke-width="1.2" stroke-dasharray="4 6" opacity="0.75"/>`;
  }

  const head = idx >= 0 ? renderProbe(points[idx].x, points[idx].y) : '';

  const legendText = legend
    ?? (points.length ? `${cols} WEEKS · LIVE · GITHUB · SIGNAL TRAIL` : 'NO SIGNAL · OFFLINE');

  const label = `<text x="28" y="38" font-family="JetBrains Mono" font-size="11" letter-spacing="3" fill="#d4a85a">§ ${escapeXml(title.toUpperCase())}</text>`;
  const footer = `<text x="${W / 2}" y="${H - 18}" text-anchor="middle" font-family="JetBrains Mono" font-size="9" letter-spacing="2" fill="#6b5a3a">${escapeXml(legendText)}</text>`;

  return box(W, H, label + grid + trail + head + footer, { embedFonts, fontsDir });
}

module.exports = {
  renderTransmissionTrail,
  levelOf,
  LEVELS,
  H,
  W,
  visitIndex,
};
