from flask import Flask, render_template, redirect, url_for, abort, send_from_directory
import os
import requests
import base64
import markdown
from flask import Markup

app = Flask(__name__)

# Project data structure
projects = [
    {
        "id": "frostbyte",
        "title": "Frostbyte - A lightweight data versioning tool",
        "slug": "frostbyte",
        "description": "Frostbyte: Efficient cold storage for data files with versioning and zero cloud dependencies. Compress, track, and restore datasets through a simple CLI designed for data scientists.",
        "image": "frostbyte/frostbyte_card.png",
        "template": "frostbyte.html",
        "github": "https://github.com/utkuyucel/Frostbyte"
    },
    {
        "id": "fundratetracker",
        "title": "Fed Fund Rate Tracker",
        "slug": "fundratetracker",
        "description": "A comprehensive financial analytics platform for tracking and analyzing Federal Reserve interest rate changes",
        "image": "fundratetracker/fundratetracker.png",
        "template": "fundratetracker.html",
        "github": "https://github.com/utkuyucel/fundratetracker"
    },
    {
        "id": "spa",
        "title": "Stock Performance Analyzer",
        "slug": "stock_performance_analyzer",
        "description": "A sophisticated tool leveraging Python for comprehensive stock performance analysis, enabling data-driven investment decisions through visual insights.",
        "image": "spa/spa.png",
        "template": "spa.html",
        "github": "https://github.com/utkuyucel/Stock_Heatmap_Visualization"
    },
    {
        "id": "volume_analyzer",
        "title": "ETL - Volume Analyzer",
        "slug": "volume_analyzer",
        "description": "An advanced ETL pipeline for processing large datasets with automated clustering and regression analytics, yielding actionable business intelligence.",
        "image": "volume_analyzer/volume.png",
        "template": "volume_analyzer.html",
        "github": "https://github.com/utkuyucel/Analyzing_volume_data"
    },
    {
        "id": "url_shortener",
        "title": "URL Shortener",
        "slug": "url_shortener",
        "description": "An advanced URL shortener with custom slugs",
        "image": "url_shortener/url_shortener.png",
        "template": "url_shortener.html",
        "github": "https://github.com/utkuyucel/url-shortener"
    },
    {
        "id": "clustering",
        "title": "Cryptocurrency Exchange Clustering",
        "slug": "exchange_clustering",
        "description": "Strategic pattern identification through advanced clustering algorithms, uncovering hidden relationships in cryptocurrency exchange data.",
        "image": "clustering/cls.png",
        "template": "clustering.html",
        "github": "https://github.com/utkuyucel/exchange_clustering"
    },
    {
        "id": "betting_engine",
        "title": "Betting Engine",
        "slug": "betting_engine",
        "description": "A sophisticated statistical engine implementing advanced probability models to calculate odds and simulate betting outcomes with high precision.",
        "image": "betting_engine/betting.png",
        "template": "betting_engine.html",
        "github": "https://github.com/utkuyucel/betting-engine"
    }
]

# Data Infrastructure Designs data structure
designs = [
    {
        "id": "influencer_ranking",
        "title": "Influencer Ranking System Design",
        "slug": "influencer_ranking",
        "image": "data_designs/influencer_ranking.png",
        "template": "data_designs/influencer_ranking.html",
        "github": "https://github.com/utkuyucel/data-infra-designs/blob/main/influencer_ranking_system_design.md"
    }
]

# Create a lookup dictionary for quick access to project data
project_lookup = {project["slug"]: project for project in projects}

# Create a lookup dictionary for quick access to design data  
design_lookup = {design["slug"]: design for design in designs}

@app.route("/")
def index():
    return render_template("index.html", projects=projects, designs=designs)

@app.route("/project/<slug>")
def project_detail(slug):
    # Look up the project by slug
    if slug not in project_lookup:
        abort(404)
    
    project = project_lookup[slug]
    
    # Try to fetch README content if GitHub URL exists
    readme_content = None
    if project.get("github"):
        # Fetch the repository's README directly using the API
        readme_content = get_github_readme(project["github"])
    
    return render_template(
        project["template"], 
        project=project,
        readme_content=readme_content
    )

@app.route("/design/<slug>")
def design_detail(slug):
    # Look up the design by slug
    if slug not in design_lookup:
        abort(404)
    
    design = design_lookup[slug]
    
    # Redirect directly to the GitHub URL
    return redirect(design["github"])  # Directly redirect to GitHub link

# Function to fetch README content from GitHub
def get_github_readme(repo_url):
    """
    Fetch the README.md content from a GitHub repository or direct markdown file
    
    Args:
        repo_url: The GitHub repository URL or direct file URL
    
    Returns:
        HTML content of the README/markdown or None if not found
    """
    try:
        # Check if this is a direct file URL (contains /blob/)
        if '/blob/' in repo_url:
            # Convert blob URL to raw URL
            raw_url = repo_url.replace('/blob/', '/').replace('github.com', 'raw.githubusercontent.com')
            
            # Make direct request to raw file
            response = requests.get(raw_url)
            
            if response.status_code == 200:
                decoded_content = response.text
                
                # Extract owner/repo for relative image paths
                parts = repo_url.split('/')
                github_index = parts.index('github.com')
                owner = parts[github_index + 1]
                repo = parts[github_index + 2]
                branch = parts[github_index + 4]  # usually 'main' or 'master'
                
                raw_base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
                
                # Fix relative image paths
                import re
                decoded_content = re.sub(
                    r'!\[(.*?)\]\((?!https?://)(.*?)\)', 
                    rf'![\1]({raw_base_url}\2)', 
                    decoded_content
                )
                
                # Process mermaid diagrams
                decoded_content = re.sub(
                    r'```mermaid\n(.*?)```',
                    r'<div class="mermaid">\n\1</div>',
                    decoded_content, 
                    flags=re.DOTALL
                )
                
                # Convert markdown to HTML
                html_content = Markup(markdown.markdown(
                    decoded_content, 
                    extensions=[
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.tables',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.extra'
                    ],
                    output_format='html5'
                ))
                return html_content
            else:
                print(f"Failed to fetch file. Status code: {response.status_code}")
                return None
        
        # Original README fetching logic for repository URLs
        # Extract owner and repo from URL
        parts = repo_url.rstrip('/').split('/')
        if 'github.com' not in parts:
            return None
            
        # Find the index of 'github.com' in the URL parts
        github_index = parts.index('github.com')
        if github_index + 2 >= len(parts):
            return None
            
        owner = parts[github_index + 1]
        repo = parts[github_index + 2].split('.')[0]  # Remove .git if present
        
        # Calculate base URL for raw content (used for fixing relative image paths)
        raw_base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/"
        
        # Always fetch the repository's README file
        api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        
        # Make the request with appropriate headers
        headers = {}
        # Add GitHub token if available (for higher rate limits)
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            # Get content and decode from base64
            content = response.json().get('content', '')
            if not content:
                return None
                
            decoded_content = base64.b64decode(content).decode('utf-8')
            
            # Fix relative image paths by replacing them with absolute GitHub URLs
            # This regex looks for Markdown image syntax with relative paths
            import re
            decoded_content = re.sub(
                r'!\[(.*?)\]\((?!https?://)(.*?)\)', 
                rf'![\1]({raw_base_url}\2)', 
                decoded_content
            )
            
            # Process mermaid diagrams - wrap them with special div for client-side rendering
            # Look for mermaid code blocks and mark them for later processing
            decoded_content = re.sub(
                r'```mermaid\n(.*?)```',
                r'<div class="mermaid">\n\1</div>',
                decoded_content, 
                flags=re.DOTALL
            )
            
            # Convert markdown to HTML with extensions for code highlighting
            html_content = Markup(markdown.markdown(
                decoded_content, 
                extensions=[
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.tables',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.extra'
                ],
                output_format='html5'
            ))
            return html_content
        else:
            print(f"Failed to fetch README. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching README: {str(e)}")
        return None

# SEO and web crawler management routes
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

# Legacy routes for backward compatibility
@app.route("/stock_performance_analyzer")
def spa():
    return redirect(url_for("project_detail", slug="stock_performance_analyzer"))

@app.route("/volume_analyzer")
def volume_analyzer():
    return redirect(url_for("project_detail", slug="volume_analyzer"))

@app.route("/exchange_clustering")
def exchange_clustering():
    return redirect(url_for("project_detail", slug="exchange_clustering"))

@app.route("/betting_engine")
def betting_engine():
    return redirect(url_for("project_detail", slug="betting_engine"))

@app.route("/frostbyte")
def frostbyte():
    return redirect(url_for("project_detail", slug="frostbyte"))

@app.route("/url_shortener")
def url_shortener():
    return redirect(url_for("project_detail", slug="url_shortener"))

@app.route("/fundratetracker")
def fundratetracker():
    return redirect(url_for("project_detail", slug="fundratetracker"))

@app.route('/mermaid-test')
def mermaid_test():
    with open('/home/utku/portfolio-project/mermaid_test.md', 'r') as f:
        content = f.read()
        
    # Process mermaid diagrams
    import re
    content = re.sub(
        r'```mermaid\n(.*?)```',
        r'<div class="mermaid">\n\1</div>',
        content, 
        flags=re.DOTALL
    )
    
    # Convert markdown to HTML
    html_content = Markup(markdown.markdown(
        content, 
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.codehilite',
            'markdown.extensions.extra'
        ],
        output_format='html5'
    ))
    
    return render_template('project_layout.html', project={'title': 'Mermaid Test'}, readme_html=html_content)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
