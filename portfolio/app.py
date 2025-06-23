from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Dict
import os
import re
import base64

import requests
import markdown
from flask import Flask, render_template, redirect, url_for, abort, send_from_directory, Markup

app = Flask(__name__)

# Constants
GITHUB_API_BASE = "https://api.github.com/repos"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
MARKDOWN_EXTENSIONS = [
    'markdown.extensions.fenced_code',
    'markdown.extensions.tables', 
    'markdown.extensions.codehilite',
    'markdown.extensions.extra'
]

@dataclass(frozen=True)
class Project:
    """Immutable project data structure"""
    id: str
    title: str
    slug: str
    description: str
    image: str
    template: str
    github: str

@dataclass(frozen=True) 
class Design:
    """Immutable design data structure"""
    id: str
    title: str
    slug: str
    image: str
    template: str
    github: str

# Project data structure
PROJECTS = [
    Project(
        id="frostbyte",
        title="Frostbyte - A lightweight data versioning tool",
        slug="frostbyte", 
        description="Frostbyte: Efficient cold storage for data files with versioning and zero cloud dependencies. Compress, track, and restore datasets through a simple CLI designed for data scientists.",
        image="frostbyte/frostbyte_card.png",
        template="frostbyte.html",
        github="https://github.com/utkuyucel/Frostbyte"
    ),
    Project(
        id="fundratetracker",
        title="Fed Fund Rate Tracker",
        slug="fundratetracker",
        description="A comprehensive financial analytics platform for tracking and analyzing Federal Reserve interest rate changes",
        image="fundratetracker/fundratetracker.png",
        template="fundratetracker.html", 
        github="https://github.com/utkuyucel/fundratetracker"
    ),
    Project(
        id="ibb-traffic-prediction",
        title="Traffic Prediction for IBB",
        slug="ibbtrafficprediction",
        description="A comprehensive traffic prediction system for Istanbul using real-time data collection, machine learning models, and API services for traffic condition analysis and forecasting.",
        image="ibb-traffic-prediction/traffic.png",
        template="traffic-prediction.html", 
        github="https://github.com/utkuyucel/ibb-traffic-prediction"
    ),
    Project(
        id="spa",
        title="Stock Performance Analyzer",
        slug="stock_performance_analyzer",
        description="A sophisticated tool leveraging Python for comprehensive stock performance analysis, enabling data-driven investment decisions through visual insights.",
        image="spa/spa.png",
        template="spa.html",
        github="https://github.com/utkuyucel/Stock_Heatmap_Visualization"
    ),
    Project(
        id="volume_analyzer", 
        title="ETL - Volume Analyzer",
        slug="volume_analyzer",
        description="An advanced ETL pipeline for processing large datasets with automated clustering and regression analytics, yielding actionable business intelligence.",
        image="volume_analyzer/volume.png",
        template="volume_analyzer.html",
        github="https://github.com/utkuyucel/Analyzing_volume_data"
    ),
    Project(
        id="url_shortener",
        title="URL Shortener", 
        slug="url_shortener",
        description="An advanced URL shortener with custom slugs",
        image="url_shortener/url_shortener.png",
        template="url_shortener.html",
        github="https://github.com/utkuyucel/url-shortener"
    ),
    Project(
        id="clustering",
        title="Cryptocurrency Exchange Clustering",
        slug="exchange_clustering",
        description="Strategic pattern identification through advanced clustering algorithms, uncovering hidden relationships in cryptocurrency exchange data.",
        image="clustering/cls.png",
        template="clustering.html",
        github="https://github.com/utkuyucel/exchange_clustering"
    ),
    Project(
        id="betting_engine",
        title="Betting Engine",
        slug="betting_engine", 
        description="A sophisticated statistical engine implementing advanced probability models to calculate odds and simulate betting outcomes with high precision.",
        image="betting_engine/betting.png",
        template="betting_engine.html",
        github="https://github.com/utkuyucel/betting-engine"
    )
]

# Data Infrastructure Designs data structure
DESIGNS = [
    Design(
        id="influencer_ranking",
        title="Influencer Ranking System Design", 
        slug="influencer_ranking",
        image="data_designs/influencer_ranking.png",
        template="data_designs/influencer_ranking.html",
        github="https://github.com/utkuyucel/data-infra-designs/blob/main/influencer_ranking_system_design.md"
    )
]

# Create lookup dictionaries using comprehensions for O(1) access
PROJECT_LOOKUP: Dict[str, Project] = {project.slug: project for project in PROJECTS}
DESIGN_LOOKUP: Dict[str, Design] = {design.slug: design for design in DESIGNS}

@app.route("/")
def index():
    return render_template("index.html", projects=PROJECTS, designs=DESIGNS)

@app.route("/project/<slug>")
def project_detail(slug):
    project = PROJECT_LOOKUP.get(slug)
    if not project:
        abort(404)
    
    readme_content = None
    if project.github:
        readme_content = get_github_readme(project.github)
    
    return render_template(
        project.template, 
        project=project,
        readme_content=readme_content
    )

@app.route("/design/<slug>")
def design_detail(slug):
    design = DESIGN_LOOKUP.get(slug)
    if not design:
        abort(404)
    
    return redirect(design.github)

def _extract_repo_info(repo_url: str) -> Optional[tuple]:
    """Extract owner and repo name from GitHub URL"""
    parts = repo_url.rstrip('/').split('/')
    if 'github.com' not in parts:
        return None
    
    try:
        github_index = parts.index('github.com')
        if github_index + 2 >= len(parts):
            return None
        
        owner = parts[github_index + 1]
        repo = parts[github_index + 2].split('.')[0]  # Remove .git if present
        return owner, repo
    except (ValueError, IndexError):
        return None

def _fix_relative_paths(content: str, raw_base_url: str) -> str:
    """Fix relative image paths in markdown content"""
    return re.sub(
        r'!\[(.*?)\]\((?!https?://)(.*?)\)', 
        rf'![\1]({raw_base_url}\2)', 
        content
    )

def _process_mermaid_diagrams(content: str) -> str:
    """Convert mermaid code blocks to HTML divs"""
    return re.sub(
        r'```mermaid\n(.*?)```',
        r'<div class="mermaid">\n\1</div>',
        content, 
        flags=re.DOTALL
    )

def _convert_markdown_to_html(content: str) -> Markup:
    """Convert markdown content to HTML with extensions"""
    return Markup(markdown.markdown(
        content, 
        extensions=MARKDOWN_EXTENSIONS,
        output_format='html5'
    ))

@lru_cache(maxsize=32)
def _fetch_direct_file(raw_url: str, repo_url: str) -> Optional[str]:
    """Fetch content from direct file URL with caching"""
    try:
        response = requests.get(raw_url, timeout=10)
        if response.status_code != 200:
            return None
        
        # Extract repo info for relative paths
        parts = repo_url.split('/')
        github_index = parts.index('github.com')
        owner = parts[github_index + 1]
        repo = parts[github_index + 2]
        branch = parts[github_index + 4]
        
        raw_base_url = f"{GITHUB_RAW_BASE}/{owner}/{repo}/{branch}/"
        content = response.text
        content = _fix_relative_paths(content, raw_base_url)
        content = _process_mermaid_diagrams(content)
        
        return content
    except Exception as e:
        print(f"Error fetching direct file: {e}")
        return None

@lru_cache(maxsize=32)  
def _fetch_repo_readme(owner: str, repo: str) -> Optional[str]:
    """Fetch README from GitHub API with caching"""
    try:
        api_url = f"{GITHUB_API_BASE}/{owner}/{repo}/readme"
        headers = {}
        
        # Add GitHub token if available for higher rate limits
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        content = response.json().get('content', '')
        if not content:
            return None
            
        decoded_content = base64.b64decode(content).decode('utf-8')
        raw_base_url = f"{GITHUB_RAW_BASE}/{owner}/{repo}/main/"
        
        decoded_content = _fix_relative_paths(decoded_content, raw_base_url)
        decoded_content = _process_mermaid_diagrams(decoded_content)
        
        return decoded_content
    except Exception as e:
        print(f"Error fetching README: {e}")
        return None

def get_github_readme(repo_url: str) -> Optional[Markup]:
    """
    Fetch and convert GitHub README or markdown file to HTML
    
    Args:
        repo_url: GitHub repository URL or direct file URL
    
    Returns:
        HTML content or None if not found
    """
    try:
        # Handle direct file URLs
        if '/blob/' in repo_url:
            raw_url = repo_url.replace('/blob/', '/').replace('github.com', 'raw.githubusercontent.com')
            content = _fetch_direct_file(raw_url, repo_url)
            if content:
                return _convert_markdown_to_html(content)
            return None
        
        # Handle repository URLs
        repo_info = _extract_repo_info(repo_url)
        if not repo_info:
            return None
        
        owner, repo = repo_info
        content = _fetch_repo_readme(owner, repo)
        if content:
            return _convert_markdown_to_html(content)
        
        return None
    except Exception as e:
        print(f"Error processing GitHub content: {e}")
        return None

# SEO and web crawler management routes
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

# Legacy redirect routes for backward compatibility
LEGACY_ROUTES = [
    "stock_performance_analyzer", "volume_analyzer", "exchange_clustering",
    "betting_engine", "frostbyte", "url_shortener", "fundratetracker", "ibbtrafficprediction"
]

def create_legacy_redirect(slug: str):
    """Factory function to create legacy redirect routes"""
    def redirect_to_project():
        return redirect(url_for("project_detail", slug=slug))
    return redirect_to_project

# Register legacy routes dynamically
for route in LEGACY_ROUTES:
    app.add_url_rule(
        f"/{route}", 
        route, 
        create_legacy_redirect(route)
    )

@app.route('/mermaid-test')
def mermaid_test():
    """Test route for mermaid diagram rendering"""
    try:
        test_file_path = '/home/utku/portfolio-project/mermaid_test.md'
        with open(test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = _process_mermaid_diagrams(content)
        html_content = _convert_markdown_to_html(content)
        
        return render_template(
            'project_layout.html', 
            project={'title': 'Mermaid Test'}, 
            readme_html=html_content
        )
    except FileNotFoundError:
        abort(404)
    except Exception as e:
        print(f"Error in mermaid test: {e}")
        abort(500)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
