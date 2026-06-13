const { box, escapeXml } = require('./frame');

const LEVELS = ['#0a0805', '#1a1308', '#5a4220', '#7d5d2a', '#a37a3a', '#d4a85a'];
const CELL = 11;
const SIZE = 9;
const PAD_X = 28;
const PAD_TOP = 64;
const W = 840;

function levelOf(count) {
  if (count <= 0) return 0;
  if (count < 2) return 1;
  if (count < 5) return 2;
  if (count < 10) return 3;
  if (count < 20) return 4;
  return 5;
}

function renderScaleLegend(startX, y) {
  let cells = '';
  LEVELS.forEach((fill, i) => {
    cells += `<rect x="${startX + i * 14}" y="${y}" width="10" height="10" rx="2" fill="${fill}"/>`;
  });
  return `${cells}<text x="${startX - 4}" y="${y + 8}" text-anchor="end" font-family="JetBrains Mono" font-size="8" fill="#6b5a3a">−</text>`
    + `<text x="${startX + LEVELS.length * 14 + 6}" y="${y + 8}" font-family="JetBrains Mono" font-size="8" fill="#6b5a3a">+</text>`;
}

function renderHeatmap(weeks, opts = {}) {
  const {
    title = 'TRANSMISSION RECORD',
    legend,
    showScale = true,
  } = opts;

  const cols = weeks.length;
  const gridW = cols * CELL;
  const startX = Math.round((W - gridW) / 2);
  let cells = '';
  weeks.forEach((days, wi) => {
    days.forEach((d, di) => {
      const x = startX + wi * CELL;
      const y = PAD_TOP + di * CELL;
      cells += `<rect x="${x}" y="${y}" width="${SIZE}" height="${SIZE}" rx="2" fill="${LEVELS[levelOf(d.count)]}"/>`;
    });
  });

  const legendText = legend ?? (cols ? `${cols} WEEKS` : 'EMPTY');
  const H = PAD_TOP + 7 * CELL + (showScale ? 52 : 40);
  const label = `<text x="${PAD_X}" y="38" font-family="JetBrains Mono" font-size="11" letter-spacing="3" fill="#d4a85a">§ ${escapeXml(title.toUpperCase())}</text>`;
  const footer = `<text x="${W / 2}" y="${H - 28}" text-anchor="middle" font-family="JetBrains Mono" font-size="9" letter-spacing="2" fill="#6b5a3a">${escapeXml(legendText)}</text>`;
  const scale = showScale
    ? renderScaleLegend(W - PAD_X - LEVELS.length * 14, H - 14)
    : '';

  return box(W, H, label + cells + footer + scale);
}

module.exports = { renderHeatmap, levelOf, LEVELS };
