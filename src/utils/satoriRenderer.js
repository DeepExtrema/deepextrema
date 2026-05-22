const fs = require('fs');
const path = require('path');
const satori = require('satori').default;

const fontPath = path.join(__dirname, '../assets/fonts/Cardo-Regular.ttf');
const fontBuffer = fs.readFileSync(fontPath);

async function renderSvg(element, width, height) {
    const svg = await satori(element, {
        width,
        height,
        fonts: [
            {
                name: 'Cardo',
                data: fontBuffer,
                weight: 400,
                style: 'normal'
            }
        ]
    });
    const textContent = element.props && element.props.children ? element.props.children : '';
    if (textContent && typeof textContent === 'string') {
        return svg.replace('</svg>', `<!-- ${textContent} --></svg>`);
    }
    return svg;
}
module.exports = { renderSvg };
