// Mock Octokit and GraphQL before requiring the module
const mockSearchCommits = jest.fn();
const mockRateLimitGet = jest.fn();
const mockListForUser = jest.fn();
const mockListForOrg = jest.fn();
const mockListCommits = jest.fn();
const mockListWorkflowRunsForRepo = jest.fn();
const mockIssuesAndPullRequests = jest.fn();
const mockGraphql = jest.fn();

jest.mock('@octokit/rest', () => {
  return {
    Octokit: jest.fn().mockImplementation(() => {
      return {
        rest: {
          search: {
            commits: mockSearchCommits,
            issuesAndPullRequests: mockIssuesAndPullRequests
          },
          rateLimit: {
            get: mockRateLimitGet
          },
          repos: {
            listForUser: mockListForUser,
            listForOrg: mockListForOrg,
            listCommits: mockListCommits
          },
          actions: {
            listWorkflowRunsForRepo: mockListWorkflowRunsForRepo
          }
        }
      };
    })
  };
});

jest.mock('@octokit/graphql', () => {
  return {
    graphql: mockGraphql
  };
});

describe('GitHub Fetcher - Mock Mode', () => {
  let github;
  const originalEnv = process.env.GITHUB_TOKEN;

  beforeAll(() => {
    jest.resetModules();
    delete process.env.GITHUB_TOKEN;
    github = require('../src/utils/github');
  });

  afterAll(() => {
    process.env.GITHUB_TOKEN = originalEnv;
  });

  it('returns a number for commit counts', async () => {
    const result = await github.getCommitCount('DeepExtrema');
    expect(typeof result).toBe('number');
    expect(result).toBe(1977);
  });

  it('returns mock rate limit', async () => {
    const result = await github.getRateLimit();
    expect(result).toEqual({ remaining: 4999, limit: 5000 });
  });

  it('returns mock repos', async () => {
    const result = await github.getRepos('DeepExtrema');
    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBe(3);
    expect(result[0].name).toBe('voyager-1-telemetry');
    expect(result[0].language).toBe('Assembly');
  });

  it('returns mock recent commits', async () => {
    const result = await github.getRecentCommits('DeepExtrema', 7);
    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBeGreaterThan(0);
    expect(result[0]).toHaveProperty('sha');
    expect(result[0]).toHaveProperty('message');
  });

  it('returns mock workflow health', async () => {
    const result = await github.getWorkflowHealth('DeepExtrema', 'voyager-1-telemetry');
    expect(result).toEqual({
      status: "operational",
      sparkline: "✅✅✅✅❌✅✅✅❌✅"
    });
  });

  it('returns mock contribution calendar', async () => {
    const result = await github.getContributionCalendar('DeepExtrema');
    expect(result).toHaveProperty('totalContributions');
    expect(result).toHaveProperty('weeks');
    expect(result.totalContributions).toBe(850);
    expect(result.weeks.length).toBe(52);
  });

  it('returns mock activity metrics', async () => {
    const result = await github.getActivityMetrics('DeepExtrema', 30);
    expect(result).toEqual({
      period_days: 30,
      commits_count: 14,
      merged_prs_count: 4,
      closed_issues_count: 9,
      active_repos_count: 3,
      active_repos: expect.any(Array)
    });
  });
});

describe('GitHub Fetcher - Live Mode', () => {
  let github;
  const originalEnv = process.env.GITHUB_TOKEN;

  beforeAll(() => {
    jest.resetModules();
    process.env.GITHUB_TOKEN = 'test-token';
    github = require('../src/utils/github');
  });

  afterAll(() => {
    process.env.GITHUB_TOKEN = originalEnv;
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('calls search.commits and returns total_count', async () => {
    mockSearchCommits.mockResolvedValueOnce({
      data: { total_count: 42 }
    });

    const result = await github.getCommitCount('DeepExtrema');
    expect(mockSearchCommits).toHaveBeenCalledWith({
      q: 'user:DeepExtrema',
      per_page: 1
    });
    expect(result).toBe(42);
  });

  it('calls rateLimit.get and returns rate info', async () => {
    mockRateLimitGet.mockResolvedValueOnce({
      data: { rate: { remaining: 123, limit: 1000 } }
    });

    const result = await github.getRateLimit();
    expect(mockRateLimitGet).toHaveBeenCalled();
    expect(result).toEqual({ remaining: 123, limit: 1000 });
  });

  it('calls repos.listForUser and maps data correctly', async () => {
    mockListForUser.mockResolvedValueOnce({
      data: [
        {
          name: 'repo-1',
          created_at: '2023-01-01T00:00:00Z',
          pushed_at: '2023-01-02T00:00:00Z',
          archived: false,
          language: 'JavaScript',
          stargazers_count: 10
        }
      ]
    });

    const result = await github.getRepos('DeepExtrema');
    expect(mockListForUser).toHaveBeenCalledWith({
      username: 'DeepExtrema',
      type: 'owner',
      per_page: 100
    });
    expect(result).toEqual([
      {
        name: 'repo-1',
        created_at: '2023-01-01T00:00:00Z',
        pushed_at: '2023-01-02T00:00:00Z',
        archived: false,
        language: 'JavaScript',
        stargazers_count: 10
      }
    ]);
  });

  it('falls back to repos.listForOrg if listForUser fails', async () => {
    mockListForUser.mockRejectedValueOnce(new Error('Not found'));
    mockListForOrg.mockResolvedValueOnce({
      data: [
        {
          name: 'org-repo',
          created_at: '2023-01-01T00:00:00Z',
          pushed_at: '2023-01-02T00:00:00Z',
          archived: true,
          language: 'Python',
          stargazers_count: 20
        }
      ]
    });

    const result = await github.getRepos('DeepExtrema');
    expect(mockListForUser).toHaveBeenCalled();
    expect(mockListForOrg).toHaveBeenCalledWith({
      org: 'DeepExtrema',
      per_page: 100
    });
    expect(result).toEqual([
      {
        name: 'org-repo',
        created_at: '2023-01-01T00:00:00Z',
        pushed_at: '2023-01-02T00:00:00Z',
        archived: true,
        language: 'Python',
        stargazers_count: 20
      }
    ]);
  });

  it('calls repos.listCommits for active repos and maps data correctly', async () => {
    mockListForUser.mockResolvedValueOnce({
      data: [
        {
          name: 'active-repo',
          created_at: '2023-01-01T00:00:00Z',
          pushed_at: new Date().toISOString(),
          archived: false,
          language: 'Rust',
          stargazers_count: 5
        }
      ]
    });

    mockListCommits.mockResolvedValueOnce({
      data: [
        {
          sha: '1234567890abcdef',
          commit: {
            message: 'feat: add awesome feature\nwith description',
            author: {
              name: 'John Doe',
              date: '2023-01-02T12:00:00Z'
            }
          },
          html_url: 'https://github.com/DeepExtrema/active-repo/commit/1234567890abcdef'
        }
      ]
    });

    const result = await github.getRecentCommits('DeepExtrema', 7);
    expect(mockListCommits).toHaveBeenCalledWith({
      owner: 'DeepExtrema',
      repo: 'active-repo',
      since: expect.any(String),
      per_page: 20
    });
    expect(result).toEqual([
      {
        sha: '1234567',
        message: 'feat: add awesome feature',
        repo: 'active-repo',
        author: 'John Doe',
        date: '2023-01-02T12:00:00Z',
        url: 'https://github.com/DeepExtrema/active-repo/commit/1234567890abcdef'
      }
    ]);
  });

  it('calls listWorkflowRunsForRepo and returns status and sparkline', async () => {
    mockListWorkflowRunsForRepo.mockResolvedValueOnce({
      data: {
        workflow_runs: [
          { conclusion: 'success', status: 'completed' },
          { conclusion: 'failure', status: 'completed' },
          { conclusion: null, status: 'in_progress' }
        ]
      }
    });

    const result = await github.getWorkflowHealth('DeepExtrema', 'active-repo');
    expect(mockListWorkflowRunsForRepo).toHaveBeenCalledWith({
      owner: 'DeepExtrema',
      repo: 'active-repo',
      per_page: 10
    });
    expect(result).toEqual({
      status: 'operational',
      sparkline: '✅❌⏳'
    });
  });

  it('calls graphql and returns contribution calendar info', async () => {
    mockGraphql.mockResolvedValueOnce({
      user: {
        contributionsCollection: {
          contributionCalendar: {
            totalContributions: 150,
            weeks: [
              {
                contributionDays: [
                  { color: '#fff', contributionCount: 1, date: '2023-01-01', weekday: 0 }
                ]
              }
            ]
          }
        }
      }
    });

    const result = await github.getContributionCalendar('DeepExtrema');
    expect(mockGraphql).toHaveBeenCalledWith(expect.any(String), {
      login: 'DeepExtrema',
      headers: {
        authorization: 'token test-token'
      }
    });
    expect(result).toEqual({
      totalContributions: 150,
      weeks: [
        {
          contributionDays: [
            { color: '#fff', contributionCount: 1, date: '2023-01-01', weekday: 0 }
          ]
        }
      ]
    });
  });

  it('calls search.issuesAndPullRequests and maps metrics correctly', async () => {
    // 1. mock getRepos
    mockListForUser.mockResolvedValue({
      data: [
        {
          name: 'repo-1',
          created_at: '2023-01-01T00:00:00Z',
          pushed_at: new Date().toISOString(),
          archived: false,
          language: 'JavaScript',
          stargazers_count: 5
        }
      ]
    });

    // 2. mock getRecentCommits -> listCommits
    mockListCommits.mockResolvedValueOnce({
      data: []
    });

    // 3. mock search.issuesAndPullRequests for PRs
    mockIssuesAndPullRequests.mockResolvedValueOnce({
      data: { total_count: 5 }
    });

    // 4. mock search.issuesAndPullRequests for Issues
    mockIssuesAndPullRequests.mockResolvedValueOnce({
      data: { total_count: 8 }
    });

    const result = await github.getActivityMetrics('DeepExtrema', 30);
    expect(result).toEqual({
      period_days: 30,
      commits_count: 0,
      merged_prs_count: 5,
      closed_issues_count: 8,
      active_repos_count: 1,
      active_repos: [
        {
          name: 'repo-1',
          pushed_at: expect.any(String),
          stargazers_count: 5,
          language: 'JavaScript'
        }
      ]
    });
  });
});
