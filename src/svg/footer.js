const { box, escapeXml } = require('./frame');

const W = 840;
const H = 160;

function renderFooter(cfg) {
  const cx = W / 2;
  const inner = `
  <g transform="translate(${cx - 26} 28)" fill="none" stroke="#8a6d34">
    <circle cx="26" cy="26" r="24" stroke-width="0.7" opacity="0.6"/>
    <circle cx="26" cy="26" r="13" stroke-width="0.9" stroke="#d4a85a"/>
    <line x1="13" y1="26" x2="39" y2="26" stroke-width="0.7" stroke="#d4a85a"/>
    <line x1="26" y1="13" x2="26" y2="39" stroke-width="0.7" stroke="#d4a85a"/>
  </g>
  <text x="${cx}" y="108" text-anchor="middle" font-family="IBM Plex Serif" font-size="15" font-style="italic" fill="#a37a3a">${escapeXml(cfg.tagline + '.')}</text>
  <text x="${cx}" y="134" text-anchor="middle" font-family="JetBrains Mono" font-size="10" letter-spacing="2" fill="#4a3f28">${escapeXml(cfg.footerStamp)}</text>`;
  return box(W, H, inner);
}

module.exports = { renderFooter, W, H };
