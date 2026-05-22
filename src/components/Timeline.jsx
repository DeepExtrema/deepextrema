const React = require('react');
const {
  GOLD,
  GOLD_BRIGHT,
  GOLD_DEEP,
  BRASS,
  BG,
  BG_PANEL,
  INK_DIM,
  INK_MID,
  INK,
  INK_BRIGHT,
  FONT_SERIF,
  FONT_MONO
} = require('../voyagerConstants');

function Timeline({ repos, minYear, maxYear, now }) {
  // Safe default values
  const currentNow = now ? new Date(now) : new Date();
  const actualMinYear = minYear || 2021;
  const actualMaxYear = maxYear || (currentNow.getFullYear() + 1);

  const minTime = new Date(Date.UTC(actualMinYear, 0, 1)).getTime();
  const maxTime = new Date(Date.UTC(actualMaxYear, 0, 1)).getTime();
  const totalSpan = maxTime - minTime;

  function getX(dateVal) {
    if (!dateVal) return 190.0;
    const dt = new Date(dateVal);
    const t = dt.getTime();
    const val = 190.0 + ((t - minTime) / totalSpan) * 950.0;
    return Math.max(190.0, Math.min(1140.0, val));
  }

  const nowX = getX(currentNow);

  const processedRepos = (repos || []).map(r => {
    const createdAt = new Date(r.created_at);
    const pushedAt = r.pushed_at ? new Date(r.pushed_at) : createdAt;
    
    const daysSincePush = (currentNow - pushedAt) / (1000 * 60 * 60 * 24);
    const isLive = !r.archived && daysSincePush < 90;

    return {
      ...r,
      createdAt,
      pushedAt,
      isLive
    };
  });

  // Sort: live first, then by created_at desc
  processedRepos.sort((a, b) => {
    const aLive = a.isLive ? 1 : 0;
    const bLive = b.isLive ? 1 : 0;
    if (aLive !== bLive) {
      return bLive - aLive;
    }
    return b.createdAt - a.createdAt;
  });

  const displayRepos = processedRepos.slice(0, 8);
  const liveCount = processedRepos.filter(r => r.isLive).length;
  const totalCount = processedRepos.length;

  const ticks = [];
  const tickLines = [];
  for (let yr = actualMinYear; yr < actualMaxYear; yr++) {
    const yrDate = new Date(Date.UTC(yr, 0, 1));
    const tickX = getX(yrDate);
    
    ticks.push(
      React.createElement('div', {
        key: `tick-${yr}`,
        style: {
          position: 'absolute',
          left: `${tickX - 15}px`,
          top: '70px',
          width: '30px',
          display: 'flex',
          justifyContent: 'center',
          fontSize: '11px',
          color: INK_MID,
          letterSpacing: '2px'
        }
      }, String(yr))
    );

    tickLines.push(
      React.createElement('div', {
        key: `line-${yr}`,
        style: {
          position: 'absolute',
          left: `${tickX}px`,
          top: '92px',
          width: '1px',
          height: '288px',
          backgroundColor: BG_PANEL
        }
      })
    );
  }

  const repoRows = [];
  displayRepos.forEach((repo, idx) => {
    const yRect = 130 + idx * 30;
    const xStart = getX(repo.createdAt);
    const xEnd = getX(repo.pushedAt);
    
    let width = Math.max(10.0, xEnd - xStart);
    let startX = xStart;
    if (startX + width > 1140.0) {
      startX = 1140.0 - width;
    }

    const lang = repo.language || 'TEXT';
    function getLangCode(l) {
      if (!l) return "TX";
      const u = l.toUpperCase();
      const mapping = {
        "PYTHON": "PY",
        "RUST": "RS",
        "TYPESCRIPT": "TS",
        "JAVASCRIPT": "JS",
        "GO": "GO",
        "HTML": "HT",
        "CSS": "CS",
        "SHELL": "SH",
        "DOCKERFILE": "DK",
        "C++": "C+",
        "C": "C"
      };
      return mapping[u] || u.slice(0, 2);
    }

    const langCode = getLangCode(lang);
    const statusText = repo.isLive ? "LIVE" : "ARCHIVED";

    let fill_color, stroke_color, text_color;
    if (repo.isLive) {
      fill_color = GOLD;
      stroke_color = GOLD_BRIGHT;
      text_color = BG_PANEL;
    } else {
      fill_color = "#2a1f0c";
      stroke_color = GOLD_DEEP;
      text_color = GOLD;
    }

    const barLabel = `${langCode} · ${statusText}`;
    let labelText = "";
    if (width >= 70.0) {
      labelText = barLabel;
    } else if (width >= 25.0) {
      labelText = langCode;
    }

    repoRows.push(
      React.createElement('div', {
        key: `row-${repo.name}`,
        style: {
          display: 'flex',
          position: 'absolute',
          left: '0px',
          top: '0px',
          width: '1200px',
          height: '420px',
          pointerEvents: 'none'
        }
      },
        React.createElement('div', {
          style: {
            position: 'absolute',
            left: '60px',
            top: `${yRect}px`,
            width: '120px',
            display: 'flex',
            justifyContent: 'flex-end',
            fontSize: '11px',
            color: INK_BRIGHT
          }
        }, repo.name),
        React.createElement('div', {
          style: {
            position: 'absolute',
            left: `${startX}px`,
            top: `${yRect}px`,
            width: `${width}px`,
            height: '16px',
            backgroundColor: fill_color,
            border: `0.8px solid ${stroke_color}`,
            display: 'flex',
            alignItems: 'center',
            paddingLeft: '7px',
            boxSizing: 'border-box'
          }
        },
          labelText ? React.createElement('span', {
            style: {
              fontSize: '9px',
              color: text_color,
              letterSpacing: '1px'
            }
          }, labelText) : null
        ),
        React.createElement('div', {
          style: {
            position: 'absolute',
            left: '1060px',
            top: `${yRect}px`,
            fontSize: '10px',
            color: repo.isLive ? GOLD : INK_MID
          }
        }, `${repo.stars || 0}★`)
      )
    );
  });

  return React.createElement('div', {
    style: {
      position: 'relative',
      width: '1200px',
      height: '420px',
      backgroundColor: BG,
      color: INK_BRIGHT,
      fontFamily: FONT_MONO,
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box',
      overflow: 'hidden'
    }
  },
    React.createElement('div', {
      style: {
        position: 'absolute',
        width: '1200px',
        height: '420px',
        opacity: 0.4,
        pointerEvents: 'none',
        display: 'flex'
      }
    },
      React.createElement('div', { style: { position: 'absolute', left: '20px', top: '40px', width: '2px', height: '2px', borderRadius: '50%', backgroundColor: GOLD } }),
      React.createElement('div', { style: { position: 'absolute', left: '120px', top: '180px', width: '1px', height: '1px', borderRadius: '50%', backgroundColor: GOLD_BRIGHT } }),
      React.createElement('div', { style: { position: 'absolute', left: '200px', top: '80px', width: '2px', height: '2px', borderRadius: '50%', backgroundColor: GOLD } }),
      React.createElement('div', { style: { position: 'absolute', left: '80px', top: '220px', width: '1px', height: '1px', borderRadius: '50%', backgroundColor: INK_MID } })
    ),

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '60px',
        top: '32px',
        fontSize: '12px',
        color: GOLD,
        letterSpacing: '3px'
      }
    }, `§ 03  ·  PROJECT  TIMELINE  ·  ${actualMinYear}–PRESENT`),

    React.createElement('div', {
      style: {
        position: 'absolute',
        right: '60px',
        top: '32px',
        fontSize: '12px',
        color: INK_DIM,
        letterSpacing: '3px',
        display: 'flex',
        justifyContent: 'flex-end'
      }
    }, `${totalCount} REPOS  ·  ${liveCount} LIVE`),

    ticks,
    tickLines,

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '190px',
        top: '92px',
        width: '950px',
        height: '1px',
        backgroundColor: INK_DIM,
        opacity: 0.5
      }
    }),

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: `${nowX}px`,
        top: '92px',
        width: '1px',
        height: '288px',
        borderLeft: `0.6px dashed ${GOLD_BRIGHT}`
      }
    }),
    React.createElement('div', {
      style: {
        position: 'absolute',
        left: `${nowX - 20}px`,
        top: '105px',
        width: '40px',
        display: 'flex',
        justifyContent: 'center',
        color: GOLD_BRIGHT,
        fontSize: '9px',
        letterSpacing: '3px'
      }
    }, "NOW"),

    repoRows,

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '60px',
        top: '390px',
        width: '14px',
        height: '6px',
        backgroundColor: GOLD
      }
    }),
    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '82px',
        top: '385px',
        fontSize: '10px',
        color: INK_DIM,
        letterSpacing: '2px'
      }
    }, "LIVE"),

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '160px',
        top: '390px',
        width: '14px',
        height: '6px',
        backgroundColor: '#2a1f0c',
        border: `0.8px solid ${GOLD_DEEP}`
      }
    }),
    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '182px',
        top: '385px',
        fontSize: '10px',
        color: INK_DIM,
        letterSpacing: '2px'
      }
    }, "ARCHIVED"),

    React.createElement('div', {
      style: {
        position: 'absolute',
        right: '60px',
        top: '385px',
        fontSize: '10px',
        color: INK_DIM,
        letterSpacing: '2px',
        display: 'flex',
        justifyContent: 'flex-end'
      }
    }, "SRC · gh.user.get_repos()")
  );
}

module.exports = Timeline;
