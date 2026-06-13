const { renderFooter } = require('../src/svg/footer');

test('footer shows tagline and stamp and a disc mark', () => {
  const svg = renderFooter({ tagline: 'Turning scattered signals into constellations', footerStamp: 'DEEPEXTREMA · SIGNAL OUTBOUND · ✦' });
  expect(svg).toContain('Turning scattered signals into constellations');
  expect(svg).toContain('DEEPEXTREMA');
  expect(svg).toContain('<circle'); // disc mark
});
