# Deep Extrema Command — GitHub Profile Redesign

**Date:** 2026-03-01
**Branch:** `claude/redesign-github-readme-HLWA3`
**Status:** Approved

---

## Concept

"Deep Space Command" — the entire GitHub profile is a live mission control interface for the DEEP EXTREMA deep-space research operation. Repos are missions. Commits are transmissions. The tech stack is onboard systems. The activity graph is flight telemetry. Visitors are viewing the command terminal.

**Target impression:** Futuristic operator + creative technologist. "This feels like a mission control interface built by someone who builds cool shit."

## Design System

### Palette

| Role | Hex | Usage |
|------|-----|-------|
| Deep Space | `#050a12` | Outermost void |
| Hull | `#0b1120` | Primary panel background |
| Instrument | `#101828` | Raised surfaces, sub-panels |
| Bulkhead | `#1a2840` | Borders, dividers, structural lines |
| Phosphor Green | `#33ff88` | Live data, nominal status, trajectory lines |
| Amber | `#ffaa22` | Callsigns, headers, caution states |
| Signal Cyan | `#00ddff` | Orbital paths, links, radar sweeps, secondary data |
| Hot Red | `#ff2244` | Alerts, live pulse dots, critical values |
| White Hot | `#eef4ff` | Peak emphasis — mission name, key numbers |
| Console Text | `#7799bb` | Body text |
| Ghost | `#2a3a50` | Dim labels, background data streams, timestamps |
| Grid Line | `#0d1a2a` | Dot grids, coordinate overlays |

### Light Mode Variants

- Base: `#eef2f8`, Panels: `#ffffff`, Borders: `#d0d8e4`, Text: `#1a2433`
- Accent colors unchanged, glow filters reduced to `stdDeviation="1"`
- Same HUD framing language — daytime cockpit display

### Typography (in SVGs)

- **Headers/Callsigns:** All caps, letter-spacing `0.2em`, amber with glow
- **Data Values:** Monospace, phosphor green, slightly larger than labels
- **Labels:** Small caps, ghost color, tight spacing
- **Callsign (username):** Large, white-hot, heavy glow bloom
- **Background data streams:** Tiny monospace hex/coordinates in grid-line color

### Visual Vocabulary

- **Radar/sweep motifs:** Circular arcs with animated sweep line (CSS-in-SVG), phosphor trail
- **Orbital trajectory lines:** Curved dotted paths in cyan connecting related data
- **Signal waveforms:** Oscilloscope sine/sawtooth as decorative borders, generated from real data
- **Star field:** Sparse randomized dots, subtle parallax layering
- **Telemetry tickers:** Fictional coordinate/frequency readouts as ambient texture
- **HUD reticle elements:** Crosshairs, range finder brackets, focus rings
- **Status dots:** `◉` with pulse animation (live), static green (nominal), ghost (inactive)
- **Symbolic markers:** `▸ ◉ ▪ ─ ┃ ◈ ⬡` — no emoji anywhere

### Panel Construction

```
╭ · · · · · · · · · · · · · · · · · · · · · · · · · ╮
·                                                     ·
·   ┌─[ SECTION_NAME ]──────────── ◉ LIVE ─ HH:MMZ ┐ ·
·   │ ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ │ ·
·   │                                                │ ·
·   │            << content area >>                  │ ·
·   │                                                │ ·
·   ├─╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌─┤ ·
·   │ STATUS LINE ── COUNTS ── SUMMARY               │ ·
·   └────────────────────────────────────────────────┘ ·
·  · · · · · · · · · · · · · · · · · · · · · · · · ·  ·
·  TELEMETRY TICKER LINE                               ·
╰ · · · · · · · · · · · · · · · · · · · · · · · · · ╯
```

### Background Texture Stack

1. Star field — random small circles, varying brightness
2. Coordinate grid — dot grid at 24px intervals in `#0d1a2a`
3. Scanlines — 2px horizontal lines, `#ffffff` at 1% opacity
4. Vignette — radial darkening at edges
5. Noise — feTurbulence at 2% opacity
6. Data rain — vertical hex columns in `#0d1a2a`, barely perceptible

### CSS Animations (in SVG)

- Radar sweep: 4s infinite rotation
- Pulse dots: 2s pulse cycle on LIVE indicators
- Signal waveform: subtle horizontal oscillation
- Blink cursor: blinking underscore after status text
- Glow breathe: 8s intensity oscillation on callsign

### Layout

- SVG width: 900px
- Section spacing: single `<br>`, no `---` dividers
- Internal panel padding: 24px
- Every SVG has dark + light variant via `<picture>` element

---

## Sections (5 total)

### 1. COMMAND HEADER (900 x 400px)

Hero SVG. The first impression.

- Center: callsign **DEEP EXTREMA** in white-hot with heavy glow
- Background: animated radar sweep circle with orbital rings
- Repo blips orbiting the radar as labeled objects
- Top-left: mission clock (UTC timestamp)
- Top-right: system status — `SYSTEMS: N NOMINAL | UPLINK: ACTIVE`
- Bottom ticker: `BEARING: 042° | RANGE: 4.2LY | SIGNAL: ████████░░ 87% | FREQ: 14.2GHz`
- Starfield + coordinate grid behind everything

### 2. MISSION LOG

Repositories as active deep-space missions. Two-column grid, 6 repos max.

Each entry:
- `◈ repo-name` in amber (mission designator)
- `▸▸ N transmissions` (commit count)
- `╰── Python · Rust · Docker` (languages)
- `last signal: Xh ago` (time since last push)
- `◉` status dot: green if active within 7 days, ghost if dormant
- Signal strength bar from commit frequency
- Star marker `★` if repo has notable star count
- Faint mission brief from repo description

Footer: `N ACTIVE MISSIONS | N DEEP PROBES | N TOTAL TRANSMISSIONS`

### 3. FLIGHT TELEMETRY

Contribution activity as spacecraft trajectory data.

- Main: oscilloscope waveform — 90-day commit frequency
  - X-axis: mission-day format `T+001` through `T+090`
  - Phosphor green line with bloom trail
  - Cyan triangle markers on peak days
  - Green gradient fill under curve
- Right mini-panel:
  - `BURN DURATION: Nd` (current streak)
  - `DISTANCE TRAVELED: N AU` (year total commits)
  - `PEAK THRUST: DayName` (most active day)
  - `CRUISE VELOCITY: N/wk` (weekly average)
- Bottom: 7-day EKG heartbeat pulse

### 4. SYSTEMS DIAGNOSTIC

Tech stack as onboard spacecraft systems. 3-column grid of diagnostic cards.

Each card:
- System name in amber: `PYTHON CORE`, `RUST ENGINE`
- Status dot: green (active), amber (recent), ghost (legacy)
- Usage bar: `████████░░░░ 67%`
- `DEPLOYED IN: N MISSIONS`
- Mini heartbeat waveform from usage frequency

Footer: `N SYSTEMS ONLINE | N STANDBY | PRIMARY: X · Y`

### 5. COMMS CHANNEL

Contact links as radio frequencies. Compact horizontal strip.

Each entry:
- `◈ PLATFORM ── FREQ NNN.NMHz ── STATUS`
- Small signal waveform icon in cyan
- Fictional frequencies deterministic from platform name hash
- Status rotates: `CHANNEL OPEN`, `UPLINK READY`, `MONITORING`

Footer: `COMMS ARRAY: N CHANNELS | ALL FREQUENCIES CLEAR | DEEP EXTREMA COMMAND OUT`

Closing README line: `◉ SYSTEM STATUS: OPERATIONAL ── ALL MISSIONS NOMINAL ── DEEP EXTREMA COMMAND`

---

## Technical Architecture

### Script Pipeline

| Script | Output | Data Source |
|--------|--------|-------------|
| `scripts/command_header.py` | `assets/command_header_{dark,light}.svg` | User profile, top repos, timestamp |
| `scripts/mission_log.py` | `assets/mission_log_{dark,light}.svg` | Repos by push date, commits, languages |
| `scripts/flight_telemetry.py` | `assets/flight_telemetry_{dark,light}.svg` | Commit activity 90 days, streak |
| `scripts/systems_diagnostic.py` | `assets/systems_diagnostic_{dark,light}.svg` | Aggregated language stats |
| `scripts/comms_channel.py` | `assets/comms_channel_{dark,light}.svg` | Config: social links + freq generation |

### Shared Modules

| Module | Purpose |
|--------|---------|
| `src/design_system.py` | **NEW** — Colors, fonts, glow filters, panel templates, textures. Single source of truth. |
| `src/svg_components.py` | **NEW** — Reusable builders: `create_panel()`, `create_status_bar()`, `create_waveform()`, `create_radar_sweep()`, `create_star_field()`, `create_signal_bar()` |
| `src/github_api.py` | **EXISTS** — Extended with commit history, language aggregation, streak calculation |
| `src/cache.py` | **EXISTS** — API response caching, prevents rate-limiting |
| `src/utils.py` | **EXISTS** — Timestamps, README section updater |

### GitHub Actions Workflow

- Trigger: every 6 hours + push to scripts/src + manual
- Sequence: checkout → Python setup → install deps → run all scripts → commit if changed
- Each script: fetch data → generate dark+light SVGs → write assets → update README section
- Bot identity: `Deep-Extrema-Bot ◈`

### README Structure

All sections use `<picture>` for dark/light switching. No dividers, no emoji headers. Panels provide visual structure. Single `<br>` between sections.

### Design Guarantees

- **Cohesion:** `design_system.py` is single source of truth for all visual constants
- **Self-sufficient:** Only GitHub API + Python stdlib + matplotlib/numpy. No CDN, no external hosting.
- **Dynamic:** All SVGs regenerate from live data every 6 hours
- **Light/dark native:** Every SVG has both variants via `<picture>`
- **Resilient:** Cache fallback on API failure
- **Extensible:** New section = new script + README marker
