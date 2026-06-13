const { renderSectionHeader } = require('../src/svg/sectionHeader');

test('section header shows number, title and optional subtitle', () => {
  const svg = renderSectionHeader({
    number: 3,
    title: 'Transmission record',
    subtitle: 'Live signal from GitHub',
  });
  expect(svg.startsWith('<svg')).toBe(true);
  expect(svg).toContain('§ 03 · TRANSMISSION RECORD');
  expect(svg).toContain('Live signal from GitHub');
});
