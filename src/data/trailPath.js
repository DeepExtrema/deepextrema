const CELL = 11;
const SIZE = 9;
const PAD_TOP = 64;
const W = 840;

function gridLayout(weekCount) {
  const gridW = weekCount * CELL;
  const startX = Math.round((W - gridW) / 2);
  return { startX, cell: CELL, size: SIZE, padTop: PAD_TOP, width: W };
}

function cellCenter(startX, weekIdx, dayIdx) {
  return {
    x: startX + weekIdx * CELL + SIZE / 2,
    y: PAD_TOP + dayIdx * CELL + SIZE / 2,
  };
}

function buildTrailPath(weeks) {
  const layout = gridLayout(weeks.length || 52);
  const points = [];

  weeks.forEach((days, wi) => {
    days.forEach((d, di) => {
      if (d.count > 0) {
        const { x, y } = cellCenter(layout.startX, wi, di);
        points.push({ date: d.date, count: d.count, week: wi, day: di, x, y });
      }
    });
  });

  return { points, layout };
}

module.exports = { buildTrailPath, gridLayout, cellCenter, CELL, SIZE, PAD_TOP, W };
