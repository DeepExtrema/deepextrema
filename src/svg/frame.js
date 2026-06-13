const { fontDefs } = require('../fonts');

const BORDER = '#3a2c12';
const BG = '#000000';

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, (c) => (
    { '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' }[c]
  ));
}

function box(width, height, inner, opts = {}) {
  const { radius = 10, border = BORDER, bg = BG } = opts;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" `
    + `viewBox="0 0 ${width} ${height}" role="img">`
    + `<defs>${fontDefs()}</defs>`
    + `<rect x="0.5" y="0.5" width="${width - 1}" height="${height - 1}" rx="${radius}" `
    + `fill="${bg}" stroke="${border}" stroke-width="1"/>`
    + inner
    + `</svg>`;
}

module.exports = { box, escapeXml, BORDER, BG };
