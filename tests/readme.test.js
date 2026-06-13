const fs = require('fs');
const path = require('path');

test('README references every generated asset and wraps tiles/buttons in links', () => {
  const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');
  const assets = ['hero.svg', 'about.svg', 'heatmap.svg', 'footer.svg',
    'work-signal-scout.svg', 'work-data-quality.svg', 'work-ask-my-paper.svg', 'work-donna.svg',
    'btn-github.svg', 'btn-website.svg', 'btn-parallax.svg'];
  assets.forEach((a) => expect(readme).toContain(`assets/${a}`));
  // tiles/buttons wrap the image in an anchor pointing to the right URL
  expect(readme).toContain('href="https://github.com/DeepExtrema/signal-scout"');
  expect(readme).toContain('href="https://taimoorawan.dev"');
});
