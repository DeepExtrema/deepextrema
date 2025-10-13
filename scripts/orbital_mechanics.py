#!/usr/bin/env python3
"""
🪐 Orbital Mechanics Simulator
Physics-based repo visualization
"""

import os
import math
from github import Github

def create_orbital_visualization(username):
    """Create orbital mechanics visualization using matplotlib"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        
        g = Github(os.getenv('GITHUB_TOKEN'))
        user = g.get_user(username)
        
        repos = list(user.get_repos()[:12])
        if not repos:
            print("No repositories found")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0B0C10')
        ax.set_facecolor('#0B0C10')
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)
        ax.axis('off')
        
        # Central "star" (your profile)
        ax.scatter([0], [0], s=500, c='#9333EA', marker='*', zorder=10)
        ax.text(0, -10, username, ha='center', fontsize=12, color='white', weight='bold')
        
        # Plot repos as orbiting bodies
        for i, repo in enumerate(repos):
            if repo.fork:
                continue
                
            angle = (i / len(repos)) * 2 * math.pi
            distance = 30 + (repo.stargazers_count * 2)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            size = max(50, repo.stargazers_count * 10)
            
            ax.scatter([x], [y], s=size, c='#6EE7B7', alpha=0.7, zorder=5)
            ax.text(x, y-distance*0.15, repo.name[:15], ha='center', fontsize=8, color='white')
            
            # Draw orbit line
            orbit_x = [distance * math.cos(a) for a in [angle - 0.3, angle, angle + 0.3]]
            orbit_y = [distance * math.sin(a) for a in [angle - 0.3, angle, angle + 0.3]]
            ax.plot(orbit_x, orbit_y, color='#3B82F6', alpha=0.3, linewidth=1, zorder=1)
        
        # Save
        os.makedirs("assets", exist_ok=True)
        plt.savefig('assets/orbital_mechanics.png', dpi=150, transparent=True, bbox_inches='tight')
        plt.close()
        
        print("✅ Generated orbital mechanics visualization")
    except ImportError:
        print("Warning: matplotlib not available, skipping orbital mechanics")
    except Exception as e:
        print(f"Error creating orbital mechanics: {e}")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    create_orbital_visualization(username)

