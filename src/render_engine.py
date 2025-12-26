import random
import datetime

# --- AESTHETIC PALETTE ---
COLORS = {
    "bg": "#0B0C10",
    "surface": "#1C1F26",
    "cyan": "#6EE7B7",
    "blue": "#3B82F6",
    "violet": "#9333EA",
    "orange": "#F59E0B",
    "text": "#ECEFF4",
    "text_dim": "#6B7280"
}

CSS_STYLES = f"""
    <style>
        .bg {{ fill: {COLORS['bg']}; }}
        .surface {{ fill: {COLORS['surface']}; fill-opacity: 0.6; stroke: {COLORS['blue']}; stroke-width: 1px; stroke-opacity: 0.3; }}
        .text {{ font-family: 'Courier New', monospace; fill: {COLORS['text']}; font-size: 12px; }}
        .label {{ font-family: sans-serif; fill: {COLORS['text_dim']}; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }}
        .glow-cyan {{ filter: url(#glow-cyan); }}
        .glow-blue {{ filter: url(#glow-blue); }}
        .accent-cyan {{ fill: {COLORS['cyan']}; }}
        .accent-orange {{ fill: {COLORS['orange']}; }}
        .accent-violet {{ fill: {COLORS['violet']}; }}
    </style>
    <defs>
        <filter id="glow-cyan" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-blue" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
    </defs>
"""

class RenderEngine:
    def create_header(self, stats):
        """Generates 1) Constellation Header"""
        width, height = 800, 180
        stars = ""
        # Procedural Starfield
        for _ in range(60):
            x, y = random.randint(0, width), random.randint(0, height)
            opacity = random.uniform(0.2, 0.8)
            size = random.uniform(0.5, 1.5)
            stars += f'<circle cx="{x}" cy="{y}" r="{size}" fill="white" opacity="{opacity}" />'
            
        # Constellation Lines (Abstract connections)
        lines = ""
        for _ in range(5):
            x1, y1 = random.randint(100, 700), random.randint(20, 160)
            x2, y2 = x1 + random.randint(-50, 50), y1 + random.randint(-50, 50)
            lines += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS["blue"]}" stroke-width="0.5" opacity="0.4" />'

        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            {CSS_STYLES}
            <rect width="100%" height="100%" class="bg" />
            {stars}
            {lines}
            
            <rect x="0" y="{height-25}" width="100%" height="25" fill="{COLORS['surface']}" />
            <line x1="0" y1="{height-25}" x2="100%" y2="{height-25}" stroke="{COLORS['cyan']}" stroke-width="1" opacity="0.5" />
            
            <text x="20" y="{height-10}" class="text" style="font-size: 10px;">
                LAST SYNC: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC | SYSTEMS: OPERATIONAL | THEME: NOMINAL
            </text>
        </svg>"""
        return svg

    def create_hud(self, metrics):
        """Generates 4) Flight Telemetry HUD"""
        width, height = 800, 220
        
        def card(x, y, title, content_svg):
            return f"""
            <g transform="translate({x}, {y})">
                <rect width="380" height="90" rx="4" class="surface" />
                <text x="10" y="20" class="label">{title}</text>
                <g transform="translate(10, 35)">{content_svg}</g>
            </g>
            """

        # Card 1: Activity Orbit (Mock sparkline)
        orbit_svg = f'<polyline points="0,40 30,35 60,42 90,20 120,25 150,10 180,30" fill="none" stroke="{COLORS["cyan"]}" stroke-width="2" class="glow-cyan"/>'
        
        # Card 2: Velocity
        velocity_svg = f"""
            <text x="0" y="20" class="text" font-size="20">PRs: {metrics['prs_merged']}</text>
            <text x="100" y="20" class="text" font-size="20">Issues: {metrics['issues_closed']}</text>
            <line x1="0" y1="35" x2="360" y2="35" stroke="{COLORS['orange']}" stroke-width="2" stroke-dasharray="4" />
        """
        
        # Card 3: Load
        load_svg = f"""
            <text x="0" y="20" class="text">Open Issues: {metrics['open_issues']}</text>
            <rect x="0" y="30" width="{min(metrics['open_issues']*10, 300)}" height="6" fill="{COLORS['blue']}" />
        """

        # Card 4: Thrusters (Languages)
        langs = metrics.get('languages', {})
        thruster_svg = ""
        offset = 0
        for lang, pct in list(langs.items())[:3]:
            width_bar = pct * 2 # scale factor
            thruster_svg += f"""
                <text x="0" y="{offset+10}" class="text" font-size="10">{lang}</text>
                <rect x="80" y="{offset+2}" width="{width_bar}" height="8" fill="{COLORS['violet']}" />
                <text x="{85+width_bar}" y="{offset+10}" class="label">{pct}%</text>
            """
            offset += 20

        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            {CSS_STYLES}
            <rect width="100%" height="100%" class="bg" />
            {card(10, 10, "ACTIVITY ORBIT [30D]", orbit_svg)}
            {card(410, 10, "VELOCITY [7D]", velocity_svg)}
            {card(10, 110, "SYSTEM LOAD", load_svg)}
            {card(410, 110, "THRUSTERS ENGAGED", thruster_svg)}
        </svg>"""
        return svg

    def create_evolution(self, history_data):
        """Generates 5) Evolution Map (Line Chart)"""
        width, height = 800, 200
        # Assume history_data is a list of dicts: [{'date':..., 'stars':...}, ...]
        # Logic to normalize data and draw polyline would go here.
        # Simplified placeholder for brevity:
        points = ""
        if history_data:
            max_val = max(d['stars'] for d in history_data) + 1
            step_x = width / len(history_data)
            for i, d in enumerate(history_data):
                x = i * step_x
                y = height - (d['stars'] / max_val * (height - 40)) - 20
                points += f"{x},{y} "

        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            {CSS_STYLES}
            <rect width="100%" height="100%" class="bg" />
            <text x="10" y="20" class="label">EVOLUTION TRAJECTORY [STARS]</text>
            
            <line x1="0" y1="{height/2}" x2="{width}" y2="{height/2}" stroke="#333" stroke-width="1" />
            
            <polyline points="{points}" fill="none" stroke="{COLORS['cyan']}" stroke-width="2" class="glow-cyan" />
            
            <polygon points="0,{height} {points} {width},{height}" fill="{COLORS['cyan']}" opacity="0.1" />
        </svg>"""
        return svg
