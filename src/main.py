import os
from data_stream import DataStream
from render_engine import RenderEngine

def main():
    token = os.environ.get("GITHUB_TOKEN")
    # Removed exception raise for token to allow local testing if needed
    
    print("🚀 Engaging Cockpit Systems...")
    
    # 1. Init Systems
    stream = DataStream(token)
    renderer = RenderEngine()
    
    # 2. Pull Telemetry
    # If standard fetch fails, use dummy data handled inside class
    try:
        metrics = stream.get_metrics()
        signals = stream.get_signals()
        history = stream.update_blackbox(metrics)
    except Exception as e:
        print(f"⚠️ Telemetry Acquisition Failed: {e}")
        metrics = {}
        signals = {}
        history = []
    
    # 3. Render Visuals
    os.makedirs("assets", exist_ok=True)
    
    try:
        # Generate Header
        with open("assets/header.svg", "w", encoding='utf-8') as f:
            f.write(renderer.create_header(metrics))
            
        # Generate HUD
        with open("assets/hud.svg", "w", encoding='utf-8') as f:
            f.write(renderer.create_hud(metrics))
            
        # Generate Signals
        with open("assets/signals.svg", "w", encoding='utf-8') as f:
            f.write(renderer.create_signal_row(signals))
            
        # Generate Evolution Map
        with open("assets/evolution.svg", "w", encoding='utf-8') as f:
            f.write(renderer.create_evolution(history))
            
        print("✅ Systems Nominal. Assets Generated.")
    except Exception as e:
        print(f"❌ Rendering Systems Failure: {e}")
        raise e

if __name__ == "__main__":
    main()
