const { box, escapeXml } = require('../src/svg/frame');

test('escapeXml encodes special characters', () => {
  expect(escapeXml(`a<b>&'"`)).toBe('a&lt;b&gt;&amp;&apos;&quot;');
});

test('box produces a well-formed svg with background, border and font defs', () => {
  const svg = box(400, 200, '<text x="10" y="10">hi</text>');
  expect(svg.startsWith('<svg')).toBe(true);
  expect(svg).toContain('width="400"');
  expect(svg).toContain('viewBox="0 0 400 200"');
  expect(svg).toContain('@font-face');          // fonts embedded
  expect(svg).toContain('stroke="#3a2c12"');    // gold border
  expect(svg).toContain('rx="10"');             // rounded
  expect(svg).toContain('>hi<');                // inner content present
  expect(svg.trim().endsWith('</svg>')).toBe(true);
});
