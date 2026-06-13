const { box, escapeXml } = require('./frame');

const W = 840;

function renderSectionHeader({ num, number, title, subtitle }) {
  const sectionNum = escapeXml(String(num ?? number ?? '00').padStart(2, '0'));
  const label = escapeXml(String(title).toUpperCase());
  const H = subtitle ? 78 : 58;
  const ruleY = H - 10;

  const subtitleSvg = subtitle
    ? `<text x="56" y="48" font-family="IBM Plex Serif" font-size="12" font-style="italic" fill="#6b5a3a">${escapeXml(subtitle)}</text>`
    : '';

  const inner = `
  <circle cx="42" cy="26" r="2.5" fill="#d4a85a" opacity="0.55"/>
  <text x="56" y="30" font-family="JetBrains Mono" font-size="11" letter-spacing="3" fill="#d4a85a">§ ${sectionNum} · ${label}</text>
  ${subtitleSvg}
  <line x1="28" y1="${ruleY}" x2="${W - 28}" y2="${ruleY}" stroke="#3a2c12" stroke-width="1"/>
  <line x1="28" y1="${ruleY}" x2="120" y2="${ruleY}" stroke="#d4a85a" stroke-width="1" opacity="0.45"/>`;

  return box(W, H, inner, { radius: 8, bg: '#030201' });
}

module.exports = { renderSectionHeader, W };
