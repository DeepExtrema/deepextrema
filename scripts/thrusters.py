#!/usr/bin/env python3
"""
🔥 Active Thrusters - Self-Detected Tech Stack
Auto-detects languages, frameworks, databases, and tools across all repos
"""

import os
import re
from datetime import datetime, timedelta
from github import Github
from collections import Counter
import base64

def get_github_client():
    token = os.getenv('GITHUB_TOKEN')
    return Github(token)

def detect_languages(g, username):
    """👨‍💻 Languages - from GitHub Linguist API"""
    language_bytes = Counter()
    week_ago = datetime.now() - timedelta(days=7)
    
    try:
        user = g.get_user(username)
        
        for repo in user.get_repos(sort='pushed'):
            if repo.fork or repo.archived:
                continue
            
            # Check if repo has recent activity
            if repo.pushed_at and repo.pushed_at.replace(tzinfo=None) > week_ago:
                try:
                    languages = repo.get_languages()
                    for lang, bytes_count in languages.items():
                        language_bytes[lang] += bytes_count
                except:
                    pass
        
        # Calculate percentages
        total = sum(language_bytes.values())
        if total == 0:
            return []
        
        lang_percentages = [
            (lang, (bytes_count / total) * 100)
            for lang, bytes_count in language_bytes.most_common(5)
        ]
        
        return lang_percentages
    except Exception as e:
        print(f"Error detecting languages: {e}")
        return []

def detect_frameworks_libraries(g, username):
    """🧰 Frameworks/Libraries - from manifests"""
    frameworks = Counter()
    
    framework_keywords = {
        'react', 'vue', 'angular', 'svelte', 'next', 'nuxt',
        'django', 'flask', 'fastapi', 'express', 'nest',
        'tensorflow', 'pytorch', 'sklearn', 'pandas', 'numpy',
        'spring', 'dotnet', 'rails', 'laravel',
    }
    
    try:
        user = g.get_user(username)
        week_ago = datetime.now() - timedelta(days=7)
        
        for repo in user.get_repos(sort='pushed')[:20]:
            if repo.fork or repo.archived:
                continue
                
            if repo.pushed_at and repo.pushed_at.replace(tzinfo=None) > week_ago:
                manifest_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml', 'pyproject.toml']
                
                for manifest_file in manifest_files:
                    try:
                        content = repo.get_contents(manifest_file)
                        text = base64.b64decode(content.content).decode('utf-8', errors='ignore').lower()
                        
                        for keyword in framework_keywords:
                            if keyword in text:
                                frameworks[keyword] += 1
                    except:
                        continue
        
        return frameworks.most_common(5)
    except Exception as e:
        print(f"Error detecting frameworks: {e}")
        return []

def detect_databases_cloud(g, username):
    """🗄️ Databases & Cloud - from configs"""
    tech = Counter()
    
    tech_keywords = {
        'postgres': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'redis': 'Redis',
        'elasticsearch': 'Elasticsearch',
        's3': 'AWS S3',
        'dynamodb': 'DynamoDB',
        'gcs': 'Google Cloud Storage',
        'azure': 'Azure',
        'vercel': 'Vercel',
        'railway': 'Railway',
        'fly.io': 'Fly.io',
        'supabase': 'Supabase',
    }
    
    try:
        user = g.get_user(username)
        week_ago = datetime.now() - timedelta(days=7)
        
        for repo in user.get_repos(sort='pushed')[:20]:
            if repo.fork or repo.archived:
                continue
                
            if repo.pushed_at and repo.pushed_at.replace(tzinfo=None) > week_ago:
                config_files = [
                    'docker-compose.yml', 'docker-compose.yaml',
                    '.env.example', 'serverless.yml',
                ]
                
                for config_file in config_files:
                    try:
                        content = repo.get_contents(config_file)
                        text = base64.b64decode(content.content).decode('utf-8', errors='ignore').lower()
                        
                        for keyword, display_name in tech_keywords.items():
                            if keyword in text:
                                tech[display_name] += 1
                    except:
                        continue
        
        return tech.most_common(5)
    except Exception as e:
        print(f"Error detecting databases/cloud: {e}")
        return []

def detect_tools(g, username):
    """💻 Software & Tools - from CI/config"""
    tools = Counter()
    
    tool_indicators = {
        '.github/workflows': 'GitHub Actions',
        'Dockerfile': 'Docker',
        '.eslintrc': 'ESLint',
        '.prettierrc': 'Prettier',
        'jest.config': 'Jest',
        'pytest.ini': 'Pytest',
    }
    
    try:
        user = g.get_user(username)
        week_ago = datetime.now() - timedelta(days=7)
        
        for repo in user.get_repos(sort='pushed')[:20]:
            if repo.fork or repo.archived:
                continue
                
            if repo.pushed_at and repo.pushed_at.replace(tzinfo=None) > week_ago:
                try:
                    contents = repo.get_contents("")
                    repo_paths = []
                    
                    # Get file and directory names
                    for item in contents:
                        repo_paths.append(item.path)
                        if item.type == 'dir':
                            try:
                                subcontents = repo.get_contents(item.path)
                                for subitem in subcontents:
                                    repo_paths.append(subitem.path)
                            except:
                                pass
                    
                    # Check for tool indicators
                    for indicator, tool_name in tool_indicators.items():
                        if any(indicator in path for path in repo_paths):
                            tools[tool_name] += 1
                except:
                    pass
        
        return tools.most_common(5)
    except Exception as e:
        print(f"Error detecting tools: {e}")
        return []

def format_percentage_bar(percentage):
    """Create a visual percentage bar"""
    filled = int(percentage / 5)  # 20 blocks max
    empty = 20 - filled
    return f"{'█' * filled}{'░' * empty}"

def update_readme(username):
    """Update README with tech stack analysis"""
    try:
        g = get_github_client()
        
        # Detect all categories
        languages = detect_languages(g, username)
        frameworks = detect_frameworks_libraries(g, username)
        databases = detect_databases_cloud(g, username)
        tools = detect_tools(g, username)
        
        # Build section
        thrusters_section = f"""## 🔥 Active Thrusters
*Self-detected tech stack from activity in the last 7 days*

### 👨‍💻 Languages
"""
        
        if languages:
            for lang, pct in languages:
                bar = format_percentage_bar(pct)
                thrusters_section += f"**{lang}** `{bar}` {pct:.1f}%\n"
        else:
            thrusters_section += "*No recent language activity detected*\n"
        
        thrusters_section += "\n### 🧰 Frameworks & Libraries\n"
        if frameworks:
            thrusters_section += ", ".join([f"`{fw[0]}`" for fw in frameworks])
        else:
            thrusters_section += "*None detected*"
        
        thrusters_section += "\n\n### 🗄️ Databases & Cloud\n"
        if databases:
            thrusters_section += ", ".join([f"`{db[0]}`" for db in databases])
        else:
            thrusters_section += "*None detected*"
        
        thrusters_section += "\n\n### 💻 Tools & DevOps\n"
        if tools:
            thrusters_section += ", ".join([f"`{tool[0]}`" for tool in tools])
        else:
            thrusters_section += "*None detected*"
        
        thrusters_section += f"\n\n*Last scan: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n"
    except Exception as e:
        print(f"Error creating thrusters section: {e}")
        thrusters_section = f"""## 🔥 Active Thrusters
*Initializing tech stack analysis...*

*Last scan: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    # Update README
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:THRUSTERS-->.*?<!--END_SECTION:THRUSTERS-->'
    replacement = f'<!--START_SECTION:THRUSTERS-->\n{thrusters_section}\n<!--END_SECTION:THRUSTERS-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated active thrusters")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

