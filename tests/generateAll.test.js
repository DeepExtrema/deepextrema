const { injectMarkdown } = require('../scripts/generateAll');
describe('Markdown Injector', () => {
    it('replaces content between markers', () => {
        const text = 'foo <!-- MARKER_START -->old<!-- MARKER_END --> bar';
        const updated = injectMarkdown(text, 'MARKER', 'new');
        expect(updated).toBe('foo <!-- MARKER_START -->\nnew\n<!-- MARKER_END --> bar');
    });
});
