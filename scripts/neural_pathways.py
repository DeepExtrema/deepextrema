#!/usr/bin/env python3
"""
🧠 Neural Pathway Map
Commit message topic analysis and transitions
"""

import os
import re
from datetime import datetime, timedelta
from github import Github
from collections import defaultdict, Counter

def analyze_commit_topics(g, username):
    """Analyze commit messages for topic transitions"""
    # Topic keywords
    topics = {
        "API": ["api", "endpoint", "rest", "graphql", "request", "response"],
        "UI": ["ui", "frontend", "component", "style", "layout", "design"],
        "Database": ["db", "database", "sql", "query", "schema", "migration"],
        "Testing": ["test", "spec", "mock", "assert", "coverage"],
        "Docs": ["doc", "readme", "comment", "documentation"],
        "AI": ["ai", "model", "train", "gpt", "llm", "neural"]
    }
    
    try:
        user = g.get_user(username)
        two_months_ago = datetime.now() - timedelta(days=60)
        
        topic_sequence = []
        
        for repo in user.get_repos()[:15]:
            if repo.fork:
                continue
            try:
                commits = repo.get_commits(since=two_months_ago)
                for commit in commits:
                    msg = commit.commit.message.lower()
                    for topic, keywords in topics.items():
                        if any(kw in msg for kw in keywords):
                            topic_sequence.append(topic)
                            break
            except:
                pass
        
        # Calculate transitions
        transitions = defaultdict(int)
        for i in range(len(topic_sequence) - 1):
            from_topic = topic_sequence[i]
            to_topic = topic_sequence[i + 1]
            if from_topic != to_topic:
                transitions[f"{from_topic}→{to_topic}"] += 1
        
        # Top 5 transitions
        top_trans = Counter(transitions).most_common(5)
        
        return top_trans
    except Exception as e:
        print(f"Error analyzing topics: {e}")
        return []

def generate_mermaid_graph(transitions):
    """Generate Mermaid graph syntax"""
    if not transitions:
        return "graph LR\n    Start[🧠 Analyzing patterns...]"
    
    lines = ["graph LR"]
    for trans, count in transitions:
        from_t, to_t = trans.split("→")
        lines.append(f"    {from_t} -->|{count}| {to_t}")
    
    return "\n".join(lines)

def update_readme(username):
    """Update README with neural pathways"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        transitions = analyze_commit_topics(g, username)
        mermaid_graph = generate_mermaid_graph(transitions)
        
        neural_section = f"""### 🧠 Neural Pathway Map
```mermaid
{mermaid_graph}
```

*Topic transitions in commit messages (last 60 days)*  
*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    except Exception as e:
        print(f"Error creating neural pathways: {e}")
        neural_section = f"""### 🧠 Neural Pathway Map
```mermaid
graph LR
    Start[🧠 Initializing neural analysis...]
```

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:NEURAL-->.*?<!--END_SECTION:NEURAL-->'
    replacement = f'<!--START_SECTION:NEURAL-->\n{neural_section}\n<!--END_SECTION:NEURAL-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated neural pathways")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

