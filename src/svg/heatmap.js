const { box, escapeXml } = require('./frame');

const LEVELS = ['#0a0805', '#1a1308', '#5a4220', '#7d5d2a', '#a37a3a', '#d4a85a'];
const CELL = 11;   // 9px + 2px gap
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

function renderHeatmap(weeks) {
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
  const H = PAD_TOP + 7 * CELL + 40;
  const label = `<text x="${PAD_X}" y="38" font-family="JetBrains Mono" font-size="11" letter-spacing="3" fill="#d4a85a">§ TRANSMISSION RECORD</text>`;
  const legend = `<text x="${W / 2}" y="${H - 18}" text-anchor="middle" font-family="JetBrains Mono" font-size="9" letter-spacing="2" fill="#6b5a3a">${escapeXml('52 WEEKS · LIVE')}</text>`;
  return box(W, H, label + cells + legend);
}

module.exports = { renderHeatmap, levelOf, LEVELS };
