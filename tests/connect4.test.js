const {
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
  bestMove,
  renderBoardSvg,
  buildReadmeSection
} = require('../scripts/connect4');

describe('connect4 column parsing', () => {
  test('accepts letters A-G case-insensitively', () => {
    expect(parseColumn('A')).toBe(0);
    expect(parseColumn('g')).toBe(6);
    expect(parseColumn(' d ')).toBe(3);
  });

  test('accepts digits 1-7', () => {
    expect(parseColumn('1')).toBe(0);
    expect(parseColumn('7')).toBe(6);
  });

  test('rejects invalid input', () => {
    expect(parseColumn('H')).toBe(-1);
    expect(parseColumn('0')).toBe(-1);
    expect(parseColumn('8')).toBe(-1);
    expect(parseColumn('')).toBe(-1);
    expect(parseColumn(undefined)).toBe(-1);
    expect(parseColumn('AA')).toBe(-1);
  });
});

describe('connect4 board mechanics', () => {
  test('discs stack from the bottom', () => {
    const board = emptyBoard();
    expect(applyMove(board, 3, CREW)).toBe(ROWS - 1);
    expect(applyMove(board, 3, PROBE)).toBe(ROWS - 2);
    expect(board[ROWS - 1][3]).toBe(CREW);
    expect(board[ROWS - 2][3]).toBe(PROBE);
  });

  test('a full column rejects further drops', () => {
    const board = emptyBoard();
    for (let i = 0; i < ROWS; i++) {
      expect(applyMove(board, 0, CREW)).toBe(ROWS - 1 - i);
    }
    expect(applyMove(board, 0, CREW)).toBe(-1);
  });

  test('isFull detects a saturated grid', () => {
    const board = emptyBoard();
    expect(isFull(board)).toBe(false);
    for (let c = 0; c < COLS; c++) {
      for (let r = 0; r < ROWS; r++) {
        applyMove(board, c, (r + c) % 2 === 0 ? CREW : PROBE);
      }
    }
    expect(isFull(board)).toBe(true);
  });
});

describe('connect4 win detection', () => {
  test('detects a horizontal win with the winning line', () => {
    const board = emptyBoard();
    for (let c = 0; c < 4; c++) applyMove(board, c, CREW);
    const { winner, line } = checkWinner(board);
    expect(winner).toBe(CREW);
    expect(line).toHaveLength(4);
  });

  test('detects a vertical win', () => {
    const board = emptyBoard();
    for (let i = 0; i < 4; i++) applyMove(board, 2, PROBE);
    expect(checkWinner(board).winner).toBe(PROBE);
  });

  test('detects a diagonal win', () => {
    const board = emptyBoard();
    // Build a ↗ staircase for CREW in columns 0-3.
    applyMove(board, 0, CREW);
    applyMove(board, 1, PROBE);
    applyMove(board, 1, CREW);
    applyMove(board, 2, PROBE);
    applyMove(board, 2, PROBE);
    applyMove(board, 2, CREW);
    applyMove(board, 3, PROBE);
    applyMove(board, 3, PROBE);
    applyMove(board, 3, PROBE);
    applyMove(board, 3, CREW);
    expect(checkWinner(board).winner).toBe(CREW);
  });

  test('an empty board has no winner', () => {
    expect(checkWinner(emptyBoard()).winner).toBe(EMPTY);
  });
});

describe('connect4 probe AI', () => {
  test('takes an immediate winning move', () => {
    const board = emptyBoard();
    for (let i = 0; i < 3; i++) applyMove(board, 5, PROBE);
    // Crew threats elsewhere should not distract from the win.
    applyMove(board, 0, CREW);
    applyMove(board, 1, CREW);
    expect(bestMove(board, PROBE)).toBe(5);
  });

  test('blocks an immediate crew win', () => {
    const board = emptyBoard();
    // Crew threat against the left wall: A-B-C on the bottom row,
    // so the only completing square is column D.
    applyMove(board, 0, CREW);
    applyMove(board, 1, CREW);
    applyMove(board, 2, CREW);
    applyMove(board, 6, PROBE);
    expect(bestMove(board, PROBE)).toBe(3);
  });

  test('never picks a full column', () => {
    const board = emptyBoard();
    for (let i = 0; i < ROWS; i++) applyMove(board, 3, i % 2 === 0 ? CREW : PROBE);
    const move = bestMove(board, PROBE);
    expect(move).not.toBe(3);
    expect(move).toBeGreaterThanOrEqual(0);
    expect(move).toBeLessThan(COLS);
  });
});

describe('connect4 rendering', () => {
  test('board SVG contains the section header and all column labels', () => {
    const svg = renderBoardSvg(newGameState());
    expect(svg).toContain('TACTICAL');
    expect(svg).toContain('CONNECT');
    for (const letter of COL_LETTERS) {
      expect(svg).toContain(`>${letter}</text>`);
    }
  });

  test('README section links every open column to a prefilled issue', () => {
    const section = buildReadmeSection(newGameState());
    for (const letter of COL_LETTERS) {
      expect(section).toContain(`title=c4%7Cdrop%7C${letter}`);
    }
    expect(section).toContain('readme-assets/connect4.svg');
  });

  test('README section disables drop links for full columns', () => {
    const state = newGameState();
    for (let i = 0; i < ROWS; i++) applyMove(state.board, 0, CREW);
    const section = buildReadmeSection(state);
    expect(section).not.toContain('title=c4%7Cdrop%7CA');
    expect(section).toContain('title=c4%7Cdrop%7CB');
  });
});
