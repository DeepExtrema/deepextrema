const { renderProjectTile } = require('../src/svg/projectTile');

test('project tile shows name and wrapped blurb', () => {
  const svg = renderProjectTile({ name: 'Signal Scout', blurb: 'Finds the faint signal buried in the noise.' });
  expect(svg.startsWith('<svg')).toBe(true);
  expect(svg).toContain('Signal Scout');
  expect(svg).toContain('Finds the faint signal');
  expect(svg).toContain('width="408"'); // tile width
});
