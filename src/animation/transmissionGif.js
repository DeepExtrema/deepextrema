const path = require('path');
const { Resvg } = require('@resvg/resvg-js');
const { GIFEncoder, quantize, applyPalette } = require('gifenc');
const { renderTransmissionTrail, W, H } = require('../svg/transmissionTrail');

const FONTS_DIR = path.join(__dirname, '..', '..', 'assets', 'fonts');
const MONO_FONT = path.join(FONTS_DIR, 'jetbrains-mono-400.woff2');

const FPS = 12;
const LOOP_SECONDS = 5;
const FRAME_COUNT = FPS * LOOP_SECONDS;
const FRAME_DELAY_MS = Math.round(1000 / FPS);

function rasterizeFrame(svg) {
  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: W },
    font: {
      fontFiles: [MONO_FONT],
      loadSystemFonts: false,
    },
  });
  const rendered = resvg.render();
  return {
    data: rendered.pixels,
    width: rendered.width,
    height: rendered.height,
  };
}

function renderTransmissionGif(weeks, opts = {}) {
  const encoder = GIFEncoder();
  const trailOpts = {
    ...opts,
    embedFonts: false,
    fontsDir: FONTS_DIR,
  };

  for (let frame = 0; frame < FRAME_COUNT; frame += 1) {
    const progress = frame / FRAME_COUNT;
    const svg = renderTransmissionTrail(weeks, { ...trailOpts, progress });
    const { data, width, height } = rasterizeFrame(svg);
    const palette = quantize(data, 256);
    const index = applyPalette(data, palette);
    encoder.writeFrame(index, width, height, {
      palette,
      delay: FRAME_DELAY_MS,
      repeat: frame === 0 ? 0 : undefined,
    });
  }

  encoder.finish();
  return Buffer.from(encoder.bytes());
}

module.exports = {
  renderTransmissionGif,
  FPS,
  LOOP_SECONDS,
  FRAME_COUNT,
  FRAME_DELAY_MS,
  H,
  W,
};
