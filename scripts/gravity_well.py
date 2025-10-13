#!/usr/bin/env python3
"""
🧲 Gravity Well
Force-directed graph of repository dependencies
"""

import os
import json
from github import Github

def generate_gravity_data(username):
    """Generate node/link data for force-directed graph"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        user = g.get_user(username)
        
        nodes = []
        links = []
        
        repos = list(user.get_repos()[:20])
        for repo in repos:
            if repo.archived:
                continue
                
            nodes.append({
                "id": repo.name,
                "size": min(repo.stargazers_count + 5, 30),
                "color": "#6EE7B7" if not repo.fork else "#3B82F6"
            })
            
            # Link forks to parents
            if repo.fork and repo.parent:
                parent_name = repo.parent.name
                # Only link if parent is in our repo list
                if any(n["id"] == parent_name for n in nodes):
                    links.append({"source": repo.name, "target": parent_name})
        
        return {"nodes": nodes, "links": links}
    except Exception as e:
        print(f"Error generating gravity data: {e}")
        return {"nodes": [], "links": []}

def create_gravity_html(data):
    """Create HTML with D3.js visualization"""
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ margin: 0; background: #0B0C10; }}
        svg {{ width: 100%; height: 600px; }}
        .node {{ cursor: pointer; }}
        .link {{ stroke: #6EE7B7; stroke-opacity: 0.3; }}
        text {{ fill: #ECEFF4; font-size: 12px; pointer-events: none; }}
    </style>
</head>
<body>
    <svg id="gravity"></svg>
    <script>
        const data = {json.dumps(data)};
        
        const svg = d3.select("#gravity");
        const width = 800, height = 600;
        
        svg.attr("viewBox", [0, 0, width, height]);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link");
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => d.color);
        
        const label = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .text(d => d.id)
            .attr("text-anchor", "middle");
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y - 20);
        }});
        
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>"""
    
    return html_template

def create_gravity_well(username):
    """Generate gravity well visualization files"""
    try:
        data = generate_gravity_data(username)
        
        # Save JSON
        os.makedirs("assets", exist_ok=True)
        with open("assets/gravity_data.json", "w") as f:
            json.dump(data, f, indent=2)
        
        # Save HTML
        html_content = create_gravity_html(data)
        with open("assets/gravity_well.html", "w", encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Generated gravity well")
    except Exception as e:
        print(f"Error creating gravity well: {e}")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    create_gravity_well(username)

