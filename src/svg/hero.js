const { box, escapeXml } = require('./frame');
const { starfield } = require('./starfield');

const W = 840;
const H = 280;

function renderHero(cfg) {
  const tagline = escapeXml(cfg.tagline);
  // Split the display name at "Deep" | "Extrema" if it matches, else show whole name.
  let head = escapeXml(cfg.name);
  let tail = '';
  const m = /^Deep(.*)$/.exec(cfg.name);
  if (m) { head = 'Deep'; tail = escapeXml(m[1]); }

  const inner = `
  <defs>
    <radialGradient id="space" cx="50%" cy="40%" r="80%">
      <stop offset="0%" stop-color="#1a1206"/><stop offset="55%" stop-color="#0a0703"/><stop offset="100%" stop-color="#000000"/>
    </radialGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#d4a85a" stop-opacity="0.55"/><stop offset="100%" stop-color="#d4a85a" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="disc" cx="38%" cy="36%" r="68%">
      <stop offset="0%" stop-color="#f5e6b8"/><stop offset="45%" stop-color="#d4a85a"/><stop offset="100%" stop-color="#5e4a1f"/>
    </radialGradient>
  </defs>
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="9" fill="url(#space)"/>
  ${starfield(W, H, 10, 7)}
  <path d="M90 56 L150 140 L320 112 L400 44" fill="none" stroke="#d4a85a" stroke-width="0.6" opacity="0.4"/>
  <circle cx="680" cy="140" r="120" fill="url(#glow)"/>
  <circle cx="680" cy="140" r="74" fill="url(#disc)"/>
  <ellipse cx="680" cy="140" rx="106" ry="24" fill="none" stroke="#d4a85a" stroke-width="1" opacity="0.45"/>
  <path d="M115 220 Q 410 120 575 142" fill="none" stroke="#d4a85a" stroke-width="1" stroke-dasharray="3 5" opacity="0.55"/>
  <g transform="translate(115 220)" fill="none" stroke="#f5e6b8" stroke-width="1.1">
    <circle r="8" stroke-width="1.2"/><line x1="0" y1="-8" x2="0" y2="-23"/>
    <line x1="-8" y1="0" x2="-26" y2="6"/><line x1="8" y1="0" x2="26" y2="6"/>
    <circle r="2" fill="#f5e6b8" stroke="none"/>
  </g>
  <text x="60" y="124" font-family="'IBM Plex Serif',Georgia,serif" font-size="50" font-weight="500" fill="#f5e6b8" letter-spacing="-1">${head}<tspan font-style="italic" fill="#d4a85a">${tail}</tspan></text>
  <text x="62" y="156" font-family="'JetBrains Mono',monospace" font-size="11" fill="#cbb98a" letter-spacing="3" font-style="italic">${tagline}</text>`;

  return box(W, H, inner, { radius: 10 });
}

module.exports = { renderHero, W, H };
