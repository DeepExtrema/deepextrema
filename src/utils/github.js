require('dotenv').config({ quiet: true });
const { Octokit } = require('@octokit/rest');
const { graphql } = require('@octokit/graphql');

const token = process.env.GITHUB_TOKEN;
let octokit = null;

if (!token) {
  console.warn('Warning: GITHUB_TOKEN is not set. GitHub fetcher will run in Mock mode.');
} else {
  octokit = new Octokit({ auth: token });
}

/**
 * Returns total commits count or count of recent commits.
 * @param {string} owner
 * @returns {Promise<number>}
 */
async function getCommitCount(owner) {
  if (!token) {
    return 1977;
  }
  const response = await octokit.rest.search.commits({
    q: `user:${owner}`,
    per_page: 1
  });
  return response.data.total_count;
}

/**
 * Returns rate limit details.
 * @returns {Promise<{ remaining: number, limit: number }>}
 */
async function getRateLimit() {
  if (!token) {
    return { remaining: 4999, limit: 5000 };
  }
  const response = await octokit.rest.rateLimit.get();
  return {
    remaining: response.data.rate.remaining,
    limit: response.data.rate.limit
  };
}

/**
 * Returns repos of the owner.
 * @param {string} owner
 * @returns {Promise<Array<{ name: string, created_at: string, pushed_at: string, archived: boolean, language: string, stargazers_count: number }>>}
 */
async function getRepos(owner) {
  if (!token) {
    return [
      {
        name: "voyager-1-telemetry",
        created_at: "1977-09-05T12:56:00Z",
        pushed_at: new Date().toISOString(),
        archived: false,
        language: "Assembly",
        stargazers_count: 120
      },
      {
        name: "golden-record-symphony",
        created_at: "1977-08-20T12:00:00Z",
        pushed_at: new Date(Date.now() - 3600000 * 24).toISOString(),
        archived: false,
        language: "C++",
        stargazers_count: 85
      },
      {
        name: "interstellar-navigator",
        created_at: "2020-01-01T00:00:00Z",
        pushed_at: new Date(Date.now() - 3600000 * 48).toISOString(),
        archived: false,
        language: "Rust",
        stargazers_count: 250
      }
    ];
  }

  let reposData;
  try {
    const response = await octokit.rest.repos.listForUser({
      username: owner,
      type: 'owner',
      per_page: 100
    });
    reposData = response.data;
  } catch (err) {
    // Fallback to Org list if listForUser fails
    const response = await octokit.rest.repos.listForOrg({
      org: owner,
      per_page: 100
    });
    reposData = response.data;
  }

  return reposData.map(r => ({
    name: r.name,
    created_at: r.created_at,
    pushed_at: r.pushed_at,
    archived: !!r.archived,
    language: r.language || 'Unknown',
    stargazers_count: r.stargazers_count || 0
  }));
}

/**
 * Returns recent commits for the owner across active repos.
 * @param {string} owner
 * @param {number} days
 * @returns {Promise<Array<{ sha: string, message: string, repo: string, author: string, date: string, url: string }>>}
 */
async function getRecentCommits(owner, days = 7) {
  if (!token) {
    const mockCommits = [
      {
        sha: "a7b3c9d",
        message: "telemetry: recalibrate star tracker camera sensors",
        repo: "voyager-1-telemetry",
        author: "NASA Jet Propulsion Laboratory",
        date: new Date().toISOString(),
        url: `https://github.com/${owner}/voyager-1-telemetry/commit/a7b3c9d`
      },
      {
        sha: "e2f4g6h",
        message: "audio: remaster Chuck Berry's Johnny B. Goode track",
        repo: "golden-record-symphony",
        author: "Carl Sagan",
        date: new Date(Date.now() - 3600000 * 24).toISOString(),
        url: `https://github.com/${owner}/golden-record-symphony/commit/e2f4g6h`
      },
      {
        sha: "i1j3k5l",
        message: "propulsion: adjust thruster pulse duration for trajectory correction",
        repo: "interstellar-navigator",
        author: "NASA Jet Propulsion Laboratory",
        date: new Date(Date.now() - 3600000 * 48).toISOString(),
        url: `https://github.com/${owner}/interstellar-navigator/commit/i1j3k5l`
      }
    ];
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    return mockCommits.filter(c => new Date(c.date) >= cutoffDate);
  }

  const repos = await getRepos(owner);
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  const activeRepos = repos
    .filter(r => !r.archived && new Date(r.pushed_at) >= cutoffDate)
    .slice(0, 5);

  const commits = [];
  for (const repo of activeRepos) {
    try {
      const response = await octokit.rest.repos.listCommits({
        owner,
        repo: repo.name,
        since: cutoffDate.toISOString(),
        per_page: 20
      });
      for (const item of response.data) {
        commits.push({
          sha: item.sha.substring(0, 7),
          message: item.commit.message.split('\n')[0],
          repo: repo.name,
          author: item.commit.author?.name || 'Unknown',
          date: item.commit.author?.date || '',
          url: item.html_url
        });
      }
    } catch (err) {
      // Ignore errors for individual repos
    }
  }

  commits.sort((a, b) => new Date(b.date) - new Date(a.date));
  return commits;
}

/**
 * Returns workflow health status for a repo.
 * @param {string} owner
 * @param {string} repoName
 * @returns {Promise<{ status: string, sparkline: string }>}
 */
async function getWorkflowHealth(owner, repoName) {
  if (!token) {
    return {
      status: "operational",
      sparkline: "✅✅✅✅❌✅✅✅❌✅"
    };
  }

  try {
    const response = await octokit.rest.actions.listWorkflowRunsForRepo({
      owner,
      repo: repoName,
      per_page: 10
    });
    const runs = response.data.workflow_runs || [];
    if (runs.length === 0) {
      return { status: 'unknown', sparkline: '' };
    }
    const lastRun = runs[0];
    const successful = runs.filter(r => r.conclusion === 'success');
    const failed = runs.filter(r => r.conclusion === 'failure');

    let status = 'operational';
    if (lastRun.conclusion === 'success') {
      status = 'operational';
    } else if (lastRun.status === 'in_progress' || lastRun.status === 'queued') {
      status = 'running';
    } else if (failed.length > successful.length / 2) {
      status = 'degraded';
    } else {
      status = 'operational';
    }

    let sparkline = '';
    for (const run of runs.slice(0, 10)) {
      if (run.conclusion === 'success') {
        sparkline += '✅';
      } else if (run.conclusion === 'failure') {
        sparkline += '❌';
      } else if (run.status === 'in_progress' || run.status === 'queued') {
        sparkline += '⏳';
      } else {
        sparkline += '⚪';
      }
    }
    return { status, sparkline };
  } catch (err) {
    return { status: 'unknown', sparkline: '' };
  }
}

/**
 * Returns contribution calendar for a user.
 * @param {string} owner
 * @returns {Promise<{ totalContributions: number, weeks: Array }>}
 */
async function getContributionCalendar(owner) {
  if (!token) {
    const mockWeeks = [];
    const now = new Date();
    for (let i = 0; i < 52; i++) {
      const contributionDays = [];
      for (let j = 0; j < 7; j++) {
        const dayDate = new Date(now);
        dayDate.setDate(now.getDate() - (52 - i) * 7 + j);
        const contributionCount = Math.floor(Math.sin((i + j) / 5) * 4) + 2;
        const finalCount = contributionCount > 0 ? contributionCount : 0;
        let color = "#ebedf0";
        if (finalCount > 0 && finalCount <= 2) color = "#9be9a8";
        else if (finalCount > 2 && finalCount <= 4) color = "#40c463";
        else if (finalCount > 4) color = "#216e39";

        contributionDays.push({
          color,
          contributionCount: finalCount,
          date: dayDate.toISOString().split('T')[0],
          weekday: j
        });
      }
      mockWeeks.push({ contributionDays });
    }
    return {
      totalContributions: 850,
      weeks: mockWeeks
    };
  }

  const query = `
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                color
                contributionCount
                date
                weekday
              }
            }
          }
        }
      }
    }
  `;

  try {
    const response = await graphql(query, {
      login: owner,
      headers: {
        authorization: `token ${token}`
      }
    });
    const calendar = response?.user?.contributionsCollection?.contributionCalendar;
    return {
      totalContributions: calendar?.totalContributions || 0,
      weeks: calendar?.weeks || []
    };
  } catch (err) {
    return {
      totalContributions: 0,
      weeks: []
    };
  }
}

/**
 * Returns activity metrics for the owner over a period of days.
 * @param {string} owner
 * @param {number} days
 * @returns {Promise<{ period_days: number, commits_count: number, merged_prs_count: number, closed_issues_count: number, active_repos_count: number, active_repos: Array }>}
 */
async function getActivityMetrics(owner, days = 30) {
  if (!token) {
    return {
      period_days: days,
      commits_count: 14,
      merged_prs_count: 4,
      closed_issues_count: 9,
      active_repos_count: 3,
      active_repos: [
        { name: "voyager-1-telemetry", pushed_at: new Date().toISOString(), stargazers_count: 120, language: "Assembly" },
        { name: "golden-record-symphony", pushed_at: new Date().toISOString(), stargazers_count: 85, language: "C++" },
        { name: "interstellar-navigator", pushed_at: new Date().toISOString(), stargazers_count: 250, language: "Rust" }
      ]
    };
  }

  try {
    const commits = await getRecentCommits(owner, days);
    const repos = await getRepos(owner);

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    const dateStr = cutoffDate.toISOString().split('T')[0];

    const activeRepos = repos.filter(r => new Date(r.pushed_at) >= cutoffDate);
    const activeReposList = activeRepos.map(r => ({
      name: r.name,
      pushed_at: r.pushed_at,
      stargazers_count: r.stargazers_count,
      language: r.language
    }));

    const prsResponse = await octokit.rest.search.issuesAndPullRequests({
      q: `is:pr is:merged user:${owner} merged:>=${dateStr}`,
      per_page: 1
    });
    const mergedPrsCount = prsResponse.data.total_count || 0;

    const issuesResponse = await octokit.rest.search.issuesAndPullRequests({
      q: `is:issue is:closed user:${owner} closed:>=${dateStr}`,
      per_page: 1
    });
    const closedIssuesCount = issuesResponse.data.total_count || 0;

    return {
      period_days: days,
      commits_count: commits.length,
      merged_prs_count: mergedPrsCount,
      closed_issues_count: closedIssuesCount,
      active_repos_count: activeReposList.length,
      active_repos: activeReposList.slice(0, 5)
    };
  } catch (err) {
    return {
      period_days: days,
      commits_count: 0,
      merged_prs_count: 0,
      closed_issues_count: 0,
      active_repos_count: 0,
      active_repos: []
    };
  }
}

module.exports = {
  getCommitCount,
  getRateLimit,
  getRepos,
  getRecentCommits,
  getWorkflowHealth,
  getContributionCalendar,
  getActivityMetrics
};
