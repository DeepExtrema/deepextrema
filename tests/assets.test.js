const fs = require('fs');
describe('Assets', () => {
    it('should contain the Voyager header SVG', () => {
        expect(fs.existsSync('readme-assets/header.svg')).toBe(true);
    });
});
