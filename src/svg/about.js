const { box, escapeXml } = require('./frame');

const W = 840;

function wrap(text, maxChars) {
  const words = String(text).split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    if (cur && (cur.length + 1 + w.length) > maxChars) { lines.push(cur); cur = w; }
    else { cur = cur ? `${cur} ${w}` : w; }
  }
  if (cur) lines.push(cur);
  return lines;
}

function centeredLines(lines, cx, startY, lineH, attrs) {
  return lines.map((l, i) =>
    `<text x="${cx}" y="${startY + i * lineH}" text-anchor="middle" ${attrs}>${escapeXml(l)}</text>`
  ).join('');
}

function renderAbout(cfg) {
  const cx = W / 2;
  const ledeLines = wrap(cfg.about.lede, 52);
  const bodyLines = wrap(cfg.about.body, 64);
  const ledeH = ledeLines.length * 30;
  const bodyH = bodyLines.length * 24;
  const H = 56 + ledeH + 18 + bodyH + 52;

  const ledeSvg = centeredLines(ledeLines, cx, 70, 30, `font-family="IBM Plex Serif" font-size="22" font-style="italic" fill="#f5e6b8"`);
  const bodyY = 70 + ledeH + 18;
  const bodySvg = centeredLines(bodyLines, cx, bodyY, 24, `font-family="IBM Plex Serif" font-size="15" font-style="italic" fill="#dcc998"`);
  const curY = bodyY + bodyH + 30;
  const currently = `<text x="${cx}" y="${curY}" text-anchor="middle" font-family="JetBrains Mono" font-size="11" letter-spacing="1" fill="#a37a3a">${escapeXml('✦  ' + cfg.currently.text + '  ✦')}</text>`;

  return box(W, H, ledeSvg + bodySvg + currently);
}

module.exports = { renderAbout, wrap };
