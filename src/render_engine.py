import random
import datetime

# --- AESTHETIC PALETTE (High-Fidelity) ---
class Palette:
    BG = "#050B14"          # Deep space black
    SURFACE = "#0F172A"     # Panel background
    SURFACE_LIGHT = "#1E293B" # Lighter panel
    BORDER = "#334155"      # Subtle borders
    
    # Neons
    CYAN = "#06B6D4"        # Primary HUD color
    CYAN_DIM = "rgba(6, 182, 212, 0.2)"
    GREEN = "#10B981"       # Success/Operational
    GREEN_DIM = "rgba(16, 185, 129, 0.2)"
    ORANGE = "#F59E0B"      # Warning/Activity
    PURPLE = "#8B5CF6"      # AI/Data
    RED = "#EF4444"         # Error/Critical
    
    TEXT_MAIN = "#E2E8F0"
    TEXT_DIM = "#94A3B8"
    TEXT_GLOW = "#FFFFFF"

# --- REUSABLE ASSETS ---
class SVGAssets:
    @staticmethod
    def get_defs():
        """Returns complex filters and gradients"""
        return f"""
        <defs>
            <!-- FILTERS -->
            <filter id="glow-cyan" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="glow-green" x="-50%" y="-50%" width="200%" height="200%">
                 <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                 <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            
            <!-- GRADIENTS -->
            <linearGradient id="grad-surface" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{Palette.SURFACE_LIGHT};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{Palette.SURFACE};stop-opacity:1" />
            </linearGradient>
            
            <linearGradient id="grad-overlay" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{Palette.CYAN};stop-opacity:0.05" />
                <stop offset="100%" style="stop-color:{Palette.CYAN};stop-opacity:0" />
            </linearGradient>
            
            <pattern id="scanlines" patternUnits="userSpaceOnUse" width="4" height="4">
                <path d="M0,4 l4,0" stroke="#000" stroke-width="1" opacity="0.3"/>
            </pattern>
        </defs>
        <style>
            .bg {{ fill: {Palette.BG}; }}
            .panel {{ fill: url(#grad-surface); stroke: {Palette.BORDER}; stroke-width: 1px; }}
            .text {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {Palette.TEXT_MAIN}; }}
            .label {{ font-family: 'Segoe UI', monospace; fill: {Palette.TEXT_DIM}; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }}
            .value {{ font-family: 'Courier New', monospace; font-weight: bold; }}
            .glow-cyan {{ filter: url(#glow-cyan); }}
            .glow-green {{ filter: url(#glow-green); }}
        </style>
        """

    @staticmethod
    def draw_panel(x, y, w, h, title=None, glow=False):
        """Draws a sci-fi panel with cut corners"""
        corner_sz = 10
        # Path with cut corners
        path = f"""
        M {x+corner_sz},{y} 
        L {x+w-corner_sz},{y} 
        L {x+w},{y+corner_sz} 
        L {x+w},{y+h-corner_sz} 
        L {x+w-corner_sz},{y+h} 
        L {x+corner_sz},{y+h} 
        L {x},{y+h-corner_sz} 
        L {x},{y+corner_sz} 
        Z
        """
        
        stroke_color = Palette.CYAN if glow else Palette.BORDER
        stroke_width = 2 if glow else 1
        filter_attr = 'filter="url(#glow-cyan)"' if glow else ''
        
        svg = f'<path d="{path}" class="panel" stroke="{stroke_color}" stroke-width="{stroke_width}" {filter_attr}/>'
        
        # Decorative tech lines
        svg += f'<line x1="{x+20}" y1="{y+h+4}" x2="{x+w-20}" y2="{y+h+4}" stroke="{Palette.CYAN}" stroke-width="2" opacity="0.3" />'
        
        if title:
            # Title bar background
            svg += f'<path d="M {x+corner_sz},{y} L {x+w-corner_sz},{y} L {x+w},{y+24} L {x},{y+24} L {x},{y+corner_sz} Z" fill="{Palette.SURFACE_LIGHT}" opacity="0.8"/>'
            svg += f'<text x="{x+15}" y="{y+16}" class="label" fill="{Palette.CYAN}">{title}</text>'
            
            # Tiny decoration status light
            svg += f'<circle cx="{x+w-15}" cy="{y+12}" r="3" fill="{Palette.GREEN}" class="glow-green"/>'

        return svg

class RenderEngine:
    def __init__(self):
        self.assets = SVGAssets()

    def create_header(self, stats):
        """Generates 1) Cosmic Header with Planetary System"""
        width, height = 800, 200
        center_x, center_y = width / 2, height / 2 + 10
        
        # --- Procedural Planets ---
        planets = ""
        colors = [Palette.CYAN, Palette.PURPLE, Palette.ORANGE, Palette.GREEN]
        
        # Central Star
        planets += f'<circle cx="{center_x}" cy="{center_y}" r="25" fill="{Palette.CYAN}" opacity="0.2" class="glow-cyan"/>'
        planets += f'<circle cx="{center_x}" cy="{center_y}" r="10" fill="#FFF" />'
        
        # Orbits and Planets
        for i in range(1, 5):
            radius = 40 * i
            speed = (5 - i) * 10
            angle = (int(datetime.datetime.utcnow().timestamp()) % 360) / speed
            
            # Orbit ring (elliptical perspective)
            planets += f'<ellipse cx="{center_x}" cy="{center_y}" rx="{radius}" ry="{radius*0.6}" fill="none" stroke="{Palette.CYAN}" stroke-width="1" opacity="0.2" />'
            
            # Planet position (simplified math for SVG)
            # Just placing static planets for visual balance if math complex
            # But let's verify with simple placement
            px = center_x + radius # Static for now to ensure rendering safety
            py = center_y 
            
            color = colors[i % len(colors)]
            planets += f'<circle cx="{px}" cy="{py}" r="{4+i}" fill="{color}" class="glow-cyan" />'

        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            {self.assets.get_defs()}
            <rect width="100%" height="100%" class="bg" />
            
            <!-- Tech Frame -->
            <path d="M 20,20 L 780,20 L 790,30 L 790,180 L 780,190 L 20,190 L 10,180 L 10,30 Z" 
                  fill="none" stroke="{Palette.CYAN}" stroke-width="2" stroke-opacity="0.5" />
            
            <!-- Status Bar Top -->
            <rect x="300" y="5" width="200" height="15" rx="2" fill="{Palette.SURFACE_LIGHT}" stroke="{Palette.CYAN}" stroke-width="1"/>
            <text x="400" y="16" text-anchor="middle" class="label" fill="{Palette.CYAN}">SYSTEMS ONLINE</text>
            
            <!-- Planet System -->
            {planets}
            
            <!-- Bottom Data Line -->
            <text x="20" y="{height-10}" class="label">
                SYNC: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | CORE: {stats.get('core_temp', 'NOMINAL')} | ALIGN: {stats.get('align', '98%')}
            </text>
        </svg>"""
        return svg

    def create_hud(self, metrics):
        """Generates 4) Flight Telemetry HUD with 3 Columns"""
        width, height = 800, 300
        
        # Layout Config
        col_gap = 10
        cw_1 = 200 # Left: Shipping
        cw_2 = 380 # Center: Log
        cw_3 = 190 # Right: Active
        
        x1 = 10
        x2 = x1 + cw_1 + col_gap
        x3 = x2 + cw_2 + col_gap
        
        y_row1 = 40
        h_row1 = 140
        
        y_row2 = 190
        h_row2 = 100
        
        # --- COMPONENT 1: Target Locked (Shipping) ---
        target_svg = f"""
            <circle cx="100" cy="60" r="30" stroke="{Palette.ORANGE}" stroke-width="2" fill="none" opacity="0.8"/>
            <circle cx="100" cy="60" r="20" stroke="{Palette.ORANGE}" stroke-width="1" fill="none" class="glow-cyan"/>
            <line x1="70" y1="60" x2="130" y2="60" stroke="{Palette.ORANGE}" />
            <line x1="100" y1="30" x2="100" y2="90" stroke="{Palette.ORANGE}" />
            <text x="100" y="110" text-anchor="middle" class="label" fill="{Palette.ORANGE}">TARGET LOCKED</text>
            <text x="100" y="125" text-anchor="middle" class="text" font-size="14">v2.5.0 Release</text>
            <rect x="20" y="130" width="160" height="4" fill="{Palette.SURFACE_LIGHT}"/>
            <rect x="20" y="130" width="140" height="4" fill="{Palette.ORANGE}"/>
        """
        
        # --- COMPONENT 2: Recent Log (Console) ---
        log_lines = metrics.get('logs', [])
        console_txt = ""
        for i, line in enumerate(log_lines[:4]):
            color = Palette.GREEN if "Merged" in line else Palette.TEXT_DIM
            console_txt += f'<text x="10" y="{20 + (i*20)}" class="text" font-family="Courier New" font-size="11" fill="{color}">> {line}</text>'
            
        console_svg = f"""
            <rect x="10" y="10" width="360" height="100" fill="#000" opacity="0.3"/>
            <g transform="translate(10, 20)">{console_txt}</g>
        """

        # --- COMPONENT 3: Active Fronts ---
        fronts = metrics.get('active_fronts', [])
        fronts_svg = ""
        for i, f in enumerate(fronts[:3]):
            fronts_svg += f"""
                <g transform="translate(10, {15 + i*40})">
                    <rect x="0" y="0" width="170" height="30" rx="2" fill="{Palette.SURFACE_LIGHT}" stroke="{Palette.BORDER}"/>
                    <circle cx="15" cy="15" r="4" fill="{Palette.CYAN}" class="glow-cyan"/>
                    <text x="30" y="18" class="text" font-size="11">{f}</text>
                </g>
            """

        # --- COMPONENT 4: Telemetry Gauges (Row 2) ---
        # Gauge 1: Activity
        gauge1 = f"""
            <text x="10" y="20" class="label">ACTIVITY</text>
            <polyline points="10,80 30,70 50,75 70,40 90,50 110,30 130,60" 
                      fill="none" stroke="{Palette.CYAN}" stroke-width="2" class="glow-cyan"/>
        """
        
        # Gauge 2: Velocity
        gauge2 = f"""
            <text x="10" y="20" class="label">VELOCITY</text>
            <text x="10" y="60" class="value" font-size="24" fill="{Palette.ORANGE}">{metrics.get('prs_merged', 0)}</text>
            <text x="10" y="80" class="label">PRS/WEEK</text>
        """
        
        # Gauge 3: Thrusters
        langs = metrics.get('languages', {})
        thrusters_svg = ""
        offset = 0
        for l, pct in list(langs.items())[:3]:
            # Ensure pct is a number
            try:
                pct_val = int(pct)
            except:
                pct_val = 0
            
            thrusters_svg += f"""
                <text x="0" y="{offset+10}" class="label">{l}</text>
                <rect x="60" y="{offset+4}" width="100" height="6" fill="{Palette.SURFACE_LIGHT}"/>
                <rect x="60" y="{offset+4}" width="{pct_val}" height="6" fill="{Palette.PURPLE}"/>
            """
            offset += 20
        

        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            {self.assets.get_defs()}
            <rect width="100%" height="100%" class="bg" />
            
            <!-- Global Frame Glow -->
            <rect width="100%" height="100%" fill="none" stroke="{Palette.BORDER}" stroke-width="10" opacity="0.1"/>
            
            <!-- ROW 1 -->
            <g transform="translate({x1}, {y_row1})">
                {self.assets.draw_panel(0, 0, cw_1, h_row1, "CURRENTLY SHIPPING")}
                <g transform="translate(10, 25)">{target_svg}</g>
            </g>
            
            <g transform="translate({x2}, {y_row1})">
                {self.assets.draw_panel(0, 0, cw_2, h_row1, "RECENT WORK LOG", glow=True)}
                <g transform="translate(0, 25)">{console_svg}</g>
            </g>
            
            <g transform="translate({x3}, {y_row1})">
                {self.assets.draw_panel(0, 0, cw_3, h_row1, "ACTIVE FRONTS")}
                <g transform="translate(0, 25)">{fronts_svg}</g>
            </g>
            
            <!-- ROW 2: TELEMETRY -->
            <g transform="translate({x1}, {y_row2})">
                 {self.assets.draw_panel(0, 0, 180, h_row2, None)}
                 <g transform="translate(10,10)">{gauge1}</g>
            </g>
            
            <g transform="translate({x1+190}, {y_row2})">
                 {self.assets.draw_panel(0, 0, 180, h_row2, None)}
                <g transform="translate(10,10)">{gauge2}</g>
            </g>
            
            <g transform="translate({x1+380}, {y_row2})">
                 {self.assets.draw_panel(0, 0, 400, h_row2, "THRUSTERS ENGAGED")}
                 <g transform="translate(20,40)">{thrusters_svg}</g>
            </g>
            
            <!-- Status Strip -->
            <rect x="10" y="5" width="780" height="30" rx="4" fill="{Palette.GREEN_DIM}" stroke="{Palette.GREEN}" />
            <text x="30" y="24" class="value" fill="{Palette.GREEN}">[✔] OPERATIONAL | LAST SUCCESSFUL RUN: JUST NOW</text>
        </svg>"""
        return svg

    def create_evolution(self, history_data):
        """Generates 5) Evolution Trajectory Map"""
        width, height = 800, 250
        
        # Grid lines
        grid = ""
        for i in range(10):
            y = 30 + (i * 20)
            grid += f'<line x1="40" y1="{y}" x2="760" y2="{y}" stroke="{Palette.BORDER}" stroke-width="0.5" opacity="0.3" />'
        
        # Data points
        points_str = ""
        points_area = "40,220 "
        
        if history_data:
            # Normalize data
            max_val = max((d['stars'] for d in history_data), default=10)
            count = len(history_data)
            step_x = 720 / max(count - 1, 1) if count > 1 else 720
            
            for i, d in enumerate(history_data):
                x = 40 + (i * step_x)
                # Flip Y (SVG coords)
                normalized_h = (d['stars'] / max_val) * 180
                y = 220 - normalized_h
                points_str += f"{x},{y} "
                points_area += f"{x},{y} "
            
            points_area += f"760,220"

        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            {self.assets.get_defs()}
            <rect width="100%" height="100%" class="bg" />
            
            <!-- Main Panel -->
            {self.assets.draw_panel(0, 0, width, height, "EVOLUTION TRAJECTORY (365D WINDOW)")}
            
            <!-- Graph Content -->
            <g transform="translate(0, 10)">
                {grid}
                
                <!-- Area Fill -->
                <polygon points="{points_area}" fill="{Palette.CYAN_DIM}" stroke="none" />
                
                <!-- Line -->
                <polyline points="{points_str}" fill="none" stroke="{Palette.CYAN}" stroke-width="3" class="glow-cyan" />
                
                <!-- Dots -->
                {''.join([f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="3" fill="#FFF"/>' for p in points_str.strip().split(" ") if p])}
            </g>
        </svg>"""
        return svg
