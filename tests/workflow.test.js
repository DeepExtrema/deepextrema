const fs = require('fs');
describe('Workflow', () => {
    it('uses node.js', () => {
        const content = fs.readFileSync('.github/workflows/update-cockpit.yml', 'utf8');
        expect(content).toContain('setup-node');
    });
});
