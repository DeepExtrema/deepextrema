const { box, escapeXml } = require('./frame');

const W = 264;
const H = 56;

function renderButton(label) {
  const text = escapeXml(String(label).toUpperCase());
  const inner = `<text x="${W / 2}" y="${H / 2 + 4}" text-anchor="middle" `
    + `font-family="JetBrains Mono" font-size="13" letter-spacing="2" fill="#f5e6b8">${text} ↗</text>`;
  return box(W, H, inner, { radius: 8, bg: '#070504' });
}

module.exports = { renderButton, W, H };
