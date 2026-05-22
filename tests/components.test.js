const React = require('react');
const Timeline = require('../src/components/Timeline');
const Heatmap = require('../src/components/Heatmap');

describe('React Components', () => {
    describe('Timeline Component', () => {
        const mockRepos = [
            {
                name: 'live-repo',
                created_at: '2025-01-01T00:00:00Z',
                pushed_at: '2026-05-20T00:00:00Z',
                archived: false,
                stars: 42,
                language: 'TypeScript'
            },
            {
                name: 'archived-repo',
                created_at: '2024-01-01T00:00:00Z',
                pushed_at: '2024-06-01T00:00:00Z',
                archived: true,
                stars: 10,
                language: 'Python'
            }
        ];

        it('renders a div as the root container', () => {
            const el = Timeline({ repos: mockRepos, minYear: 2024, maxYear: 2027, now: '2026-05-22T00:00:00Z' });
            expect(el.type).toBe('div');
            expect(el.props.style.width).toBe('1200px');
            expect(el.props.style.height).toBe('420px');
        });

        it('correctly processes and filters live vs archived repositories', () => {
            const el = Timeline({ repos: mockRepos, minYear: 2024, maxYear: 2027, now: '2026-05-22T00:00:00Z' });
            
            // Check header text for repo counts (e.g. 2 REPOS · 1 LIVE)
            const headerRight = el.props.children.find(child => 
                child && child.props && child.props.style && child.props.style.right === '60px'
            );
            expect(headerRight).toBeDefined();
            expect(headerRight.props.children).toBe('2 REPOS  ·  1 LIVE');
        });

        it('calculates position and dimensions correctly', () => {
            const el = Timeline({ repos: mockRepos, minYear: 2024, maxYear: 2027, now: '2026-05-22T00:00:00Z' });
            
            // Find the repo rows
            const repoRows = el.props.children.find(child => Array.isArray(child) && child.length > 0 && child[0].key && child[0].key.startsWith('row-'));
            expect(repoRows).toBeDefined();
            expect(repoRows.length).toBe(2);

            // First repo in sorted list should be live-repo (since live first)
            const liveRow = repoRows[0];
            expect(liveRow.key).toBe('row-live-repo');

            // Check style values for name, bar, stars
            const nameDiv = liveRow.props.children[0];
            expect(nameDiv.props.children).toBe('live-repo');

            const barDiv = liveRow.props.children[1];
            expect(barDiv.props.style.backgroundColor).toBe('#d4a85a'); // GOLD color for live
            
            const starDiv = liveRow.props.children[2];
            expect(starDiv.props.children).toBe('42★');
        });
    });

    describe('Heatmap Component', () => {
        const mockWeeks = [
            {
                contributionDays: [
                    { date: '2026-05-17', contributionCount: 0 },
                    { date: '2026-05-18', contributionCount: 1 },
                    { date: '2026-05-19', contributionCount: 4 },
                    { date: '2026-05-20', contributionCount: 8 },
                    { date: '2026-05-21', contributionCount: 12 },
                    { date: '2026-05-22', contributionCount: 20 },
                    { date: '2026-05-23', contributionCount: 0 }
                ]
            }
        ];

        it('renders a div as the root container', () => {
            const el = Heatmap({ weeks: mockWeeks, totalContributions: 45, maxStreak: 5, busiestStr: 'FRI 21:00 UTC' });
            expect(el.type).toBe('div');
            expect(el.props.style.width).toBe('1100px');
            expect(el.props.style.height).toBe('200px');
        });

        it('correctly maps contribution levels to colors', () => {
            const el = Heatmap({ weeks: mockWeeks, totalContributions: 45, maxStreak: 5, busiestStr: 'FRI 21:00 UTC' });
            
            // Find grid div
            const gridDiv = el.props.children.find(child => 
                child && child.props && child.props.style && child.props.style.left === '36px' && child.props.style.top === '56px'
            );
            expect(gridDiv).toBeDefined();
            
            const cells = gridDiv.props.children;
            expect(cells.length).toBe(7);

            // Cell index 0 has count 0 (level 0) -> bg color levels[0]
            expect(cells[0].props.style.backgroundColor).toBe('#0a0805');

            // Cell index 1 has count 1 (level 1) -> bg color levels[1]
            expect(cells[1].props.style.backgroundColor).toBe('#1a1308');

            // Cell index 5 has count 20 (level 5) -> bg color levels[5], border is GOLD_BRIGHT
            expect(cells[5].props.style.backgroundColor).toBe('#d4a85a');
            expect(cells[5].props.style.border).toBe('0.5px solid #f5e6b8');
        });

        it('renders stats in header and legend', () => {
            const el = Heatmap({ weeks: mockWeeks, totalContributions: 45, maxStreak: 5, busiestStr: 'FRI 21:00 UTC' });
            
            // Header right
            const headerRight = el.props.children.find(child => 
                child && child.props && child.props.style && child.props.style.right === '36px'
            );
            expect(headerRight).toBeDefined();
            expect(headerRight.props.children).toBe('45 COMMITS');

            // Legend info
            const legendRow = el.props.children.find(child => 
                child && child.props && child.props.style && child.props.style.top === '176px'
            );
            expect(legendRow).toBeDefined();
            
            const streakDiv = legendRow.props.children.find(child => 
                child && child.props && child.props.style && child.props.style.right === '0px'
            );
            expect(streakDiv).toBeDefined();
            expect(streakDiv.props.children).toBe('STREAK · 5 DAYS  ·  BUSIEST · FRI 21:00 UTC');
        });
    });
});
