const { renderSvg } = require('../src/utils/satoriRenderer');
describe('Satori Renderer', () => {
    it('renders a simple div to svg string', async () => {
        const element = { type: 'div', props: { style: { display: 'flex' }, children: 'Hello' } };
        const svg = await renderSvg(element, 100, 100);
        expect(svg).toContain('<svg');
        expect(svg).toContain('Hello');
    });
});
