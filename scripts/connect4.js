/**
 * § 10 · Tactical relay — Connect Four played through GitHub issues.
 *
 * CLI:
 *   node scripts/connect4.js move <column A-G|1-7> <username>
 *   node scripts/connect4.js render
 *
 * The `move` command prints ONLY the issue-comment markdown on stdout
 * (logs go to stderr) so the workflow can pipe it straight into
 * `gh issue comment --body-file`.
 */
require('dotenv').config({ quiet: true });
const fs = require('fs');
const path = require('path');
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
  FONT_SERIF,
  FONT_MONO
} = require('../src/voyagerConstants');
const { injectMarkdown, generateStars } = require('./generateAll');

const ROWS = 6;
const COLS = 7;
const EMPTY = 0;
const CREW = 1;   // visitors · gold discs
const PROBE = 2;  // house AI · deep brass discs

const COL_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
const SEARCH_ORDER = [3, 2, 4, 1, 5, 0, 6]; // center-out
const SEARCH_DEPTH = 5;

const STATE_PATH = path.join(__dirname, '../data/game/connect4.json');
const SVG_PATH = path.join(__dirname, '../readme-assets/connect4.svg');
const README_PATH = path.join(__dirname, '../README.md');
const REPO_URL = 'https://github.com/DeepExtrema/deepextrema';

// ── Game state ─────────────────────────────────────────────

function emptyBoard() {
  return Array.from({ length: ROWS }, () => Array(COLS).fill(EMPTY));
}

function newGameState(tally, recentPlayers) {
  return {
    board: emptyBoard(),
    status: 'in_progress',
    moveCount: 0,
    lastMove: null,
    winningLine: [],
    tally: tally || { crew: 0, probe: 0, draws: 0 },
    recentPlayers: recentPlayers || [],
    updated: new Date().toISOString()
  };
}

function loadState() {
  if (fs.existsSync(STATE_PATH)) {
    try {
      return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
    } catch (e) {
      console.error('Corrupt connect4 state, starting fresh:', e.message);
    }
  }
  return newGameState();
}

function saveState(state) {
  fs.mkdirSync(path.dirname(STATE_PATH), { recursive: true });
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2), 'utf8');
}

// ── Rules ──────────────────────────────────────────────────

function parseColumn(input) {
  if (input === undefined || input === null) return -1;
  const s = String(input).trim().toUpperCase();
  const letterIdx = COL_LETTERS.indexOf(s);
  if (letterIdx !== -1) return letterIdx;
  if (/^[1-7]$/.test(s)) return parseInt(s, 10) - 1;
  return -1;
}

/** Drops a disc; returns the landing row, or -1 if the column is full. */
function applyMove(board, col, player) {
  for (let r = ROWS - 1; r >= 0; r--) {
    if (board[r][col] === EMPTY) {
      board[r][col] = player;
      return r;
    }
  }
  return -1;
}

function isFull(board) {
  return board[0].every(cell => cell !== EMPTY);
}

const DIRECTIONS = [
  [0, 1],  // horizontal
  [1, 0],  // vertical
  [1, 1],  // diagonal ↘
  [1, -1]  // diagonal ↙
];

/** @returns {{winner: number, line: Array<[number, number]>}} */
function checkWinner(board) {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const player = board[r][c];
      if (player === EMPTY) continue;
      for (const [dr, dc] of DIRECTIONS) {
        const line = [[r, c]];
        for (let k = 1; k < 4; k++) {
          const nr = r + dr * k;
          const nc = c + dc * k;
          if (nr < 0 || nr >= ROWS || nc < 0 || nc >= COLS) break;
          if (board[nr][nc] !== player) break;
          line.push([nr, nc]);
        }
        if (line.length === 4) {
          return { winner: player, line };
        }
      }
    }
  }
  return { winner: EMPTY, line: [] };
}

// ── Probe AI (negamax with alpha-beta) ─────────────────────

function scoreWindow(cells, player) {
  const opponent = player === CREW ? PROBE : CREW;
  const mine = cells.filter(c => c === player).length;
  const theirs = cells.filter(c => c === opponent).length;
  if (mine > 0 && theirs > 0) return 0;
  if (mine === 3) return 120;
  if (mine === 2) return 12;
  if (mine === 1) return 1;
  if (theirs === 3) return -140;
  if (theirs === 2) return -12;
  if (theirs === 1) return -1;
  return 0;
}

function evaluate(board, player) {
  let score = 0;
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      for (const [dr, dc] of DIRECTIONS) {
        const er = r + dr * 3;
        const ec = c + dc * 3;
        if (er < 0 || er >= ROWS || ec < 0 || ec >= COLS) continue;
        const cells = [0, 1, 2, 3].map(k => board[r + dr * k][c + dc * k]);
        score += scoreWindow(cells, player);
      }
    }
  }
  // Center-column control is disproportionately valuable.
  for (let r = 0; r < ROWS; r++) {
    if (board[r][3] === player) score += 6;
    else if (board[r][3] !== EMPTY) score -= 6;
  }
  return score;
}

function negamax(board, depth, alpha, beta, player) {
  const opponent = player === CREW ? PROBE : CREW;
  const { winner } = checkWinner(board);
  if (winner === player) return 100000 + depth;
  if (winner === opponent) return -(100000 + depth);
  if (isFull(board)) return 0;
  if (depth === 0) return evaluate(board, player);

  let best = -Infinity;
  for (const col of SEARCH_ORDER) {
    const row = applyMove(board, col, player);
    if (row === -1) continue;
    const score = -negamax(board, depth - 1, -beta, -alpha, opponent);
    board[row][col] = EMPTY;
    if (score > best) best = score;
    if (best > alpha) alpha = best;
    if (alpha >= beta) break;
  }
  return best;
}

/** Picks the probe's column for the current board. Returns -1 if no move exists. */
function bestMove(board, player = PROBE) {
  const opponent = player === CREW ? PROBE : CREW;
  let bestCol = -1;
  let bestScore = -Infinity;
  for (const col of SEARCH_ORDER) {
    const row = applyMove(board, col, player);
    if (row === -1) continue;
    const score = -negamax(board, SEARCH_DEPTH - 1, -Infinity, Infinity, opponent);
    board[row][col] = EMPTY;
    if (score > bestScore) {
      bestScore = score;
      bestCol = col;
    }
  }
  return bestCol;
}

// ── Rendering ──────────────────────────────────────────────

const CELL = 62;
const DISC_R = 24;

function statusHeadline(state) {
  switch (state.status) {
    case 'in_progress': return 'YOUR MOVE';
    case 'crew_won': return 'CREW VICTORY';
    case 'probe_won': return 'PROBE VICTORY';
    case 'draw': return 'STALEMATE';
    default: return 'STANDBY';
  }
}

function statusSubline(state) {
  switch (state.status) {
    case 'in_progress': return 'The relay awaits a drop.';
    case 'crew_won': return 'Four in a row — next drop starts a new game.';
    case 'probe_won': return 'The probe prevails — next drop starts a new game.';
    case 'draw': return 'Grid saturated — next drop starts a new game.';
    default: return '';
  }
}

function renderBoardSvg(state) {
  const board = state.board;
  const winningSet = new Set((state.winningLine || []).map(([r, c]) => `${r},${c}`));

  const discs = [];
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const cx = c * CELL + CELL / 2;
      const cy = r * CELL + CELL / 2;
      const cell = board[r][c];
      if (cell === EMPTY) {
        discs.push(`      <circle cx="${cx}" cy="${cy}" r="${DISC_R}" fill="${BG_PANEL}" stroke="#1a1308" stroke-width="1.5"/>`);
      } else {
        const fill = cell === CREW ? GOLD : GOLD_DEEP;
        const stroke = winningSet.has(`${r},${c}`)
          ? GOLD_BRIGHT
          : (cell === CREW ? GOLD_BRIGHT : BRASS);
        const strokeWidth = winningSet.has(`${r},${c}`) ? 3 : 1.5;
        discs.push(`      <circle cx="${cx}" cy="${cy}" r="${DISC_R}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}"/>`);
      }
    }
  }

  const colLabels = COL_LETTERS.map((letter, c) => {
    const cx = c * CELL + CELL / 2;
    const full = board[0][c] !== EMPTY;
    const fill = full ? '#3a2f18' : INK_DIM;
    return `      <text x="${cx}" y="${ROWS * CELL + 26}" text-anchor="middle" fill="${fill}">${letter}</text>`;
  }).join('\n');

  const tally = state.tally || { crew: 0, probe: 0, draws: 0 };
  const gamesPlayed = tally.crew + tally.probe + tally.draws;
  const lastMoveStr = state.lastMove
    ? `@${state.lastMove.player} ▸ ${COL_LETTERS[state.lastMove.crewCol]}${state.lastMove.probeCol !== null && state.lastMove.probeCol !== undefined ? ` · PROBE ▸ ${COL_LETTERS[state.lastMove.probeCol]}` : ''}`
    : 'AWAITING FIRST CONTACT';

  const crew = (state.recentPlayers || []).slice(0, 4);
  const crewStr = crew.length > 0 ? crew.map(p => `@${p}`).join(' · ') : 'NO SIGHTINGS YET';

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520" width="1200" height="520">
  <rect width="1200" height="520" fill="${BG}"></rect>
  ${generateStars(1200, 520, 18, 42)}

  <!-- Title -->
  <g font-family="${FONT_MONO}" font-size="11" fill="${GOLD}" letter-spacing="3">
    <text x="36" y="36">§ 10  ·  TACTICAL  RELAY  ·  CONNECT  FOUR</text>
    <text x="1164" y="36" text-anchor="end" fill="${INK_DIM}">GAME ${gamesPlayed + (state.status === 'in_progress' ? 1 : 0)} · MOVE ${state.moveCount}</text>
  </g>

  <!-- Board -->
  <g transform="translate(70 76)">
    <rect x="-14" y="-14" width="${COLS * CELL + 28}" height="${ROWS * CELL + 28}" fill="none" stroke="${GOLD_DEEP}" stroke-width="1" opacity="0.55" rx="6"/>
    <g>
${discs.join('\n')}
    </g>
    <g font-family="${FONT_MONO}" font-size="11" letter-spacing="2">
${colLabels}
    </g>
  </g>

  <!-- Right panel -->
  <g transform="translate(600 100)" font-family="${FONT_MONO}" font-size="10" letter-spacing="2">
    <text fill="${INK_DIM}">STATUS</text>
    <text y="30" font-family="${FONT_SERIF}" font-size="26" fill="${GOLD_BRIGHT}" font-weight="500" letter-spacing="0">${statusHeadline(state)}</text>
    <text y="52" font-family="${FONT_SERIF}" font-size="13" fill="${INK_MID}" font-style="italic" letter-spacing="0">${statusSubline(state)}</text>

    <g transform="translate(0 92)">
      <text fill="${INK_DIM}">SCOREBOARD</text>
      <g transform="translate(0 28)">
        <text font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}">${tally.crew}<tspan font-size="11" fill="${INK_DIM}" font-family="${FONT_MONO}">  CREW</tspan></text>
        <text x="150" font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}">${tally.probe}<tspan font-size="11" fill="${INK_DIM}" font-family="${FONT_MONO}">  PROBE</tspan></text>
        <text x="320" font-family="${FONT_SERIF}" font-size="22" fill="${GOLD_BRIGHT}">${tally.draws}<tspan font-size="11" fill="${INK_DIM}" font-family="${FONT_MONO}">  DRAWS</tspan></text>
      </g>
    </g>

    <g transform="translate(0 172)">
      <text fill="${INK_DIM}">CALL SIGNS</text>
      <g transform="translate(0 24)">
        <circle cx="7" cy="-4" r="7" fill="${GOLD}" stroke="${GOLD_BRIGHT}"/>
        <text x="24" fill="${INK_MID}">CREW · VISITORS · YOU</text>
        <circle cx="7" cy="22" r="7" fill="${GOLD_DEEP}" stroke="${BRASS}"/>
        <text x="24" y="26" fill="${INK_MID}">PROBE · HOUSE AI · ACTIONS</text>
      </g>
    </g>

    <g transform="translate(0 252)">
      <text fill="${INK_DIM}">LAST TRANSMISSION</text>
      <text y="22" fill="${INK}" letter-spacing="1">${lastMoveStr}</text>
    </g>

    <g transform="translate(0 312)">
      <line x1="0" y1="-12" x2="540" y2="-12" stroke="${BG_PANEL}" stroke-dasharray="2 3"></line>
      <text fill="${INK_DIM}">FLIGHT CREW · RECENT OPERATORS</text>
      <text y="22" fill="${INK_MID}" letter-spacing="1">${crewStr}</text>
    </g>

    <g transform="translate(0 372)">
      <text font-family="${FONT_SERIF}" font-size="14" fill="${INK}" font-style="italic" letter-spacing="0">"Drop a disc with the ▼ links below —</text>
      <text y="20" font-family="${FONT_SERIF}" font-size="14" fill="${INK}" font-style="italic" letter-spacing="0">a GitHub Action plays the reply."</text>
    </g>
  </g>
</svg>`;
}

// ── README section ─────────────────────────────────────────

function issueUrl(letter) {
  const title = encodeURIComponent(`c4|drop|${letter}`);
  const body = encodeURIComponent(
    `Drop a gold disc into column ${letter} of the tactical relay.\n\n` +
    `Just press **Create** below — voyager-bot will make your move, answer with its own, ` +
    `update the board on the profile, and close this issue automatically.`
  );
  return `${REPO_URL}/issues/new?title=${title}&body=${body}`;
}

function buildReadmeSection(state) {
  const dropLinks = COL_LETTERS.map((letter, c) => {
    const full = state.status === 'in_progress' && state.board[0][c] !== EMPTY;
    return full ? `▼ ${letter}` : `[▼ ${letter}](${issueUrl(letter)})`;
  }).join('  ·  ');

  const crew = (state.recentPlayers || []).slice(0, 4);
  const crewLine = crew.length > 0
    ? `<sub>FLIGHT CREW · ${crew.map(p => `[@${p}](https://github.com/${p})`).join(' · ')}</sub>`
    : `<sub>FLIGHT CREW · BE THE FIRST TO TRANSMIT</sub>`;

  return `<div align="center">
  <img src="readme-assets/connect4.svg" alt="Connect Four — tactical relay board" width="100%">
</div>

<div align="center">

**DROP A DISC**  ·  ${dropLinks}

${crewLine}

<sub><i>Opening an issue makes your move. The probe answers within a minute. No login tricks — just GitHub.</i></sub>

</div>`;
}

function writeAssets(state) {
  fs.mkdirSync(path.dirname(SVG_PATH), { recursive: true });
  fs.writeFileSync(SVG_PATH, renderBoardSvg(state), 'utf8');
  console.error('✅ Generated connect4.svg');

  if (fs.existsSync(README_PATH)) {
    const readme = fs.readFileSync(README_PATH, 'utf8');
    const updated = injectMarkdown(readme, 'CONNECT4', buildReadmeSection(state));
    fs.writeFileSync(README_PATH, updated, 'utf8');
    console.error('✅ Injected CONNECT4 section in README.');
  }
}

// ── Move orchestration ─────────────────────────────────────

function recordPlayer(state, username) {
  const players = (state.recentPlayers || []).filter(p => p !== username);
  players.unshift(username);
  state.recentPlayers = players.slice(0, 6);
}

/**
 * Performs a full crew move + probe reply.
 * @returns {{ ok: boolean, comment: string, state: object }}
 */
function move(colInput, username) {
  let state = loadState();

  // A finished board stays on display until the next drop resets it.
  if (state.status !== 'in_progress') {
    state = newGameState(state.tally, state.recentPlayers);
  }

  const col = parseColumn(colInput);
  if (col === -1) {
    return {
      ok: false,
      state,
      comment:
        `🜨 Transmission garbled, @${username} — \`${colInput}\` is not a column. ` +
        `Use the **▼ drop links** under the board on [the profile](${REPO_URL}) (columns A–G).`
    };
  }

  const letter = COL_LETTERS[col];
  const row = applyMove(state.board, col, CREW);
  if (row === -1) {
    return {
      ok: false,
      state,
      comment:
        `🜨 Column **${letter}** is already packed to the rim, @${username}. ` +
        `Pick another shaft from [the board](${REPO_URL}).`
    };
  }

  state.moveCount += 1;
  recordPlayer(state, username);
  state.lastMove = { player: username, crewCol: col, probeCol: null };

  let comment;
  let result = checkWinner(state.board);
  if (result.winner === CREW) {
    state.status = 'crew_won';
    state.winningLine = result.line;
    state.tally.crew += 1;
    comment =
      `🏆 **Four in a row — the crew takes the round, @${username}!** ` +
      `Your disc in column **${letter}** sealed it. ` +
      `The scoreboard has been updated; the next drop starts a fresh game. [Return to the cockpit →](${REPO_URL})`;
  } else if (isFull(state.board)) {
    state.status = 'draw';
    state.tally.draws += 1;
    comment =
      `⚖️ **Stalemate.** Your disc in column **${letter}** filled the grid, @${username}. ` +
      `Honors even — the next drop starts a fresh game. [Return to the cockpit →](${REPO_URL})`;
  } else {
    const probeCol = bestMove(state.board, PROBE);
    const probeLetter = COL_LETTERS[probeCol];
    applyMove(state.board, probeCol, PROBE);
    state.moveCount += 1;
    state.lastMove.probeCol = probeCol;

    result = checkWinner(state.board);
    if (result.winner === PROBE) {
      state.status = 'probe_won';
      state.winningLine = result.line;
      state.tally.probe += 1;
      comment =
        `🛰 Disc received in column **${letter}**, @${username} — but the probe answered in ` +
        `**${probeLetter}** and completed four in a row. **Probe victory.** ` +
        `The next drop starts a fresh game. [Rematch? →](${REPO_URL})`;
    } else if (isFull(state.board)) {
      state.status = 'draw';
      state.tally.draws += 1;
      comment =
        `⚖️ **Stalemate.** The probe's reply in column **${probeLetter}** filled the grid. ` +
        `Honors even — the next drop starts a fresh game. [Return to the cockpit →](${REPO_URL})`;
    } else {
      comment =
        `🜨 Disc received, @${username}. You dropped into column **${letter}**; ` +
        `the probe answered in **${probeLetter}**. ` +
        `[The board has been updated →](${REPO_URL})`;
    }
  }

  state.updated = new Date().toISOString();
  return { ok: true, comment, state };
}

// ── CLI ────────────────────────────────────────────────────

function cli(argv) {
  const command = argv[0];
  if (command === 'render') {
    const state = loadState();
    saveState(state);
    writeAssets(state);
    return 0;
  }
  if (command === 'move') {
    const [, colInput, username] = argv;
    const player = username || 'anonymous-operator';
    const outcome = move(colInput, player);
    if (outcome.ok) {
      saveState(outcome.state);
      writeAssets(outcome.state);
    }
    // stdout carries only the comment markdown for the workflow.
    process.stdout.write(outcome.comment + '\n');
    return 0;
  }
  console.error('Usage: node scripts/connect4.js <move <column> <username> | render>');
  return 1;
}

module.exports = {
  ROWS,
  COLS,
  EMPTY,
  CREW,
  PROBE,
  COL_LETTERS,
  emptyBoard,
  newGameState,
  parseColumn,
  applyMove,
  isFull,
  checkWinner,
  evaluate,
  bestMove,
  renderBoardSvg,
  buildReadmeSection,
  move,
  cli
};

if (require.main === module) {
  process.exit(cli(process.argv.slice(2)));
}
