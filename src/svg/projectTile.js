const { box, escapeXml } = require('./frame');
const { wrap } = require('./about');

const W = 408;
const H = 150;

function renderProjectTile(project) {
  const blurbLines = wrap(project.blurb, 42).slice(0, 3);
  const blurb = blurbLines.map((l, i) =>
    `<text x="28" y="${78 + i * 22}" font-family="IBM Plex Serif" font-size="13" font-style="italic" fill="#6b5a3a">${escapeXml(l)}</text>`
  ).join('');

  const inner = `
  <g transform="translate(24 40)" fill="none" stroke="#d4a85a" stroke-width="1.3">
    <circle cx="8" cy="8" r="6"/><line x1="12.5" y1="12.5" x2="18" y2="18"/>
  </g>
  <text x="56" y="50" font-family="IBM Plex Serif" font-size="19" font-weight="500" fill="#f5e6b8">${escapeXml(project.name)}</text>
  <text x="${W - 28}" y="44" text-anchor="end" font-family="JetBrains Mono" font-size="12" fill="#7d5d2a">↗</text>
  ${blurb}`;

  return box(W, H, inner, { radius: 8 });
}

module.exports = { renderProjectTile, W, H };
