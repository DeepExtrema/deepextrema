const fs = require('fs');
const path = require('path');

test('README references every generated asset and wraps tiles/buttons in links', () => {
  const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');
  const assets = [
    'hero.svg', 'about.svg', 'transmission-record.svg', 'footer.svg',
    'section-work.svg', 'section-history-live.svg', 'section-contact.svg',
    'work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg',
    'btn-github.svg', 'btn-website.svg', 'btn-parallax.svg',
  ];
  assets.forEach((a) => expect(readme).toContain(`assets/${a}`));
  expect(readme).not.toContain('heatmap-example.svg');
  expect(readme).not.toContain('section-history-example.svg');
  expect(readme).toContain('href="https://github.com/DeepExtrema/signal-scout"');
  expect(readme).toContain('href="https://taimoorawan.dev"');
});
