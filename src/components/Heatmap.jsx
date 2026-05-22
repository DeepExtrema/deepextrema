const React = require('react');
const {
  GOLD,
  GOLD_BRIGHT,
  BG,
  INK_DIM,
  INK_BRIGHT,
  LEVELS,
  FONT_MONO
} = require('../voyagerConstants');

function Heatmap({ weeks, totalContributions, maxStreak, busiestStr }) {
  const actualTotal = totalContributions || 0;
  const actualStreak = maxStreak || 0;
  const actualBusiest = busiestStr || "MON 21:00 UTC";

  const allCells = [];
  (weeks || []).forEach((week, wIdx) => {
    (week.contributionDays || []).forEach((day, dIdx) => {
      const count = day.contributionCount || 0;
      let level = 0;
      if (count === 0) level = 0;
      else if (count <= 2) level = 1;
      else if (count <= 5) level = 2;
      else if (count <= 9) level = 3;
      else if (count <= 15) level = 4;
      else level = 5;

      const color = LEVELS[level];
      const strokeColor = level === 5 ? GOLD_BRIGHT : "#1f1808";

      allCells.push(
        React.createElement('div', {
          key: `cell-${wIdx}-${dIdx}`,
          style: {
            position: 'absolute',
            left: `${wIdx * 18}px`,
            top: `${dIdx * 18}px`,
            width: '16px',
            height: '16px',
            backgroundColor: color,
            border: `0.5px solid ${strokeColor}`,
            boxSizing: 'border-box'
          }
        })
      );
    });
  });

  const legendRects = [];
  LEVELS.forEach((lvl, idx) => {
    const stroke = idx === 5 ? GOLD_BRIGHT : "#1f1808";
    const xPos = 36 + idx * 14;
    legendRects.push(
      React.createElement('div', {
        key: `legend-${idx}`,
        style: {
          position: 'absolute',
          left: `${xPos}px`,
          top: '0px',
          width: '10px',
          height: '10px',
          backgroundColor: lvl,
          border: `0.5px solid ${stroke}`,
          boxSizing: 'border-box'
        }
      })
    );
  });

  const totalFormatted = actualTotal.toLocaleString('en-US');

  return React.createElement('div', {
    style: {
      position: 'relative',
      width: '1100px',
      height: '200px',
      backgroundColor: BG,
      color: GOLD,
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
        left: '36px',
        top: '22px',
        fontSize: '11px',
        color: GOLD,
        letterSpacing: '3px'
      }
    }, "§ 05  ·  TRANSMISSION  RECORD  ·  365  DAYS"),

    React.createElement('div', {
      style: {
        position: 'absolute',
        right: '36px',
        top: '22px',
        fontSize: '11px',
        color: INK_DIM,
        letterSpacing: '3px',
        display: 'flex',
        justifyContent: 'flex-end'
      }
    }, `${totalFormatted} COMMITS`),

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '36px',
        top: '56px',
        width: '954px',
        height: '126px',
        display: 'flex'
      }
    }, allCells),

    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '36px',
        top: '176px',
        width: '1028px',
        height: '14px',
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center'
      }
    },
      React.createElement('div', {
        style: {
          position: 'absolute',
          left: '0px',
          top: '0px',
          fontSize: '9px',
          color: INK_DIM,
          letterSpacing: '2px'
        }
      }, "LESS"),

      legendRects,

      React.createElement('div', {
        style: {
          position: 'absolute',
          left: '122px',
          top: '0px',
          fontSize: '9px',
          color: INK_DIM,
          letterSpacing: '2px'
        }
      }, "MORE"),

      React.createElement('div', {
        style: {
          position: 'absolute',
          right: '0px',
          top: '0px',
          fontSize: '9px',
          color: INK_DIM,
          letterSpacing: '2px',
          display: 'flex',
          justifyContent: 'flex-end'
        }
      }, `STREAK · ${actualStreak} DAYS  ·  BUSIEST · ${actualBusiest}`)
    )
  );
}

module.exports = Heatmap;
