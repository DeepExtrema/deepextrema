const fs = require('fs');
describe('Parallax Game', () => {
    it('should be located in docs/index.html', () => {
        expect(fs.existsSync('docs/index.html')).toBe(true);
    });
});
