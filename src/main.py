import os
from data_stream import DataStream
from render_engine import RenderEngine

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise Exception("Missing GITHUB_TOKEN")

    print("🚀 Engaging Cockpit Systems...")
    
    # 1. Init Systems
    stream = DataStream(token)
    renderer = RenderEngine()
    
    # 2. Pull Telemetry
    metrics = stream.get_metrics()
    history = stream.update_blackbox(metrics)
    
    # 3. Render Visuals
    os.makedirs("assets", exist_ok=True)
    
    # Generate Header
    with open("assets/header.svg", "w") as f:
        f.write(renderer.create_header(metrics))
        
    # Generate HUD
    with open("assets/hud.svg", "w") as f:
        f.write(renderer.create_hud(metrics))
        
    # Generate Evolution Map
    with open("assets/evolution.svg", "w") as f:
        f.write(renderer.create_evolution(history))
        
    print("✅ Systems Nominal. Assets Generated.")

if __name__ == "__main__":
    main()
