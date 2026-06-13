const { renderButton } = require('../src/svg/contactButton');

test('button shows uppercased label and arrow', () => {
  const svg = renderButton('GitHub');
  expect(svg.startsWith('<svg')).toBe(true);
  expect(svg).toContain('GITHUB');
  expect(svg).toContain('↗');
});
