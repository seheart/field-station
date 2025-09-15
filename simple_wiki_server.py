#!/usr/bin/env python3
"""
Simple Field Station Wiki Server
Serves markdown files as formatted text in Chrome browser
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from urllib.parse import unquote
import re

class SimpleWikiHandler(http.server.SimpleHTTPRequestHandler):
    """Simple handler for serving markdown as HTML without external dependencies"""
    
    def do_GET(self):
        # Parse the requested path
        path = self.path.lstrip('/')
        if not path or path == '/':
            path = 'WIKI_HOME.md'
        
        # Remove query parameters
        if '?' in path:
            path = path.split('?')[0]
        
        # URL decode
        path = unquote(path)
        
        # Serve markdown files as HTML
        if path.endswith('.md'):
            self.serve_markdown(path)
        elif path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg'):
            self.serve_image(path)
        else:
            # Try to find markdown file
            md_path = f"{path}.md"
            if os.path.exists(md_path):
                self.serve_markdown(md_path)
            else:
                super().do_GET()
    
    def serve_markdown(self, md_file):
        """Convert basic markdown to HTML and serve it"""
        try:
            if not os.path.exists(md_file):
                self.send_error(404, f"File not found: {md_file}")
                return
            
            # Read markdown content
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Simple markdown to HTML conversion
            html_content = self.simple_markdown_to_html(md_content)
            
            # Create full HTML page
            html_page = self.create_html_page(html_content, md_file)
            
            # Serve HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_page.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error serving {md_file}: {str(e)}")
    
    def serve_image(self, img_file):
        """Serve image files"""
        try:
            if not os.path.exists(img_file):
                self.send_error(404, f"Image not found: {img_file}")
                return
            
            # Determine content type
            if img_file.endswith('.png'):
                content_type = 'image/png'
            elif img_file.endswith('.jpg') or img_file.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'application/octet-stream'
            
            # Serve image
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            
            with open(img_file, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            self.send_error(500, f"Error serving image {img_file}: {str(e)}")
    
    def simple_markdown_to_html(self, md_content):
        """Simple markdown to HTML conversion without external libraries"""
        html = md_content
        
        # Convert headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Convert bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Convert inline code
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Convert code blocks
        html = re.sub(r'^```(\w+)?\n(.*?)^```$', r'<pre><code>\2</code></pre>', html, flags=re.MULTILINE | re.DOTALL)
        html = re.sub(r'^```\n(.*?)^```$', r'<pre><code>\1</code></pre>', html, flags=re.MULTILINE | re.DOTALL)
        
        # Convert links - markdown links to HTML
        html = re.sub(r'\[([^\]]+)\]\(([^)]+\.md)\)', r'<a href="/\2">\1</a>', html)
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
        
        # Convert bullet points
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        html = re.sub(r'</ul>\s*<ul>', '', html)  # Merge consecutive lists
        
        # Convert numbered lists
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ol>\1</ol>', html, flags=re.DOTALL)
        html = re.sub(r'</ol>\s*<ol>', '', html)  # Merge consecutive lists
        
        # Convert line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        html = html.replace('<p></p>', '')
        
        # Fix headers inside paragraphs
        html = re.sub(r'<p>(<h[1-6]>.*?</h[1-6]>)</p>', r'\1', html)
        html = re.sub(r'<p>(<ul>.*?</ul>)</p>', r'\1', html, flags=re.DOTALL)
        html = re.sub(r'<p>(<ol>.*?</ol>)</p>', r'\1', html, flags=re.DOTALL)
        html = re.sub(r'<p>(<pre>.*?</pre>)</p>', r'\1', html, flags=re.DOTALL)
        
        return html
    
    def create_html_page(self, content, md_file):
        """Create a complete HTML page with styling"""
        # Get page title from first heading or filename
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        title = title_match.group(1) if title_match else os.path.basename(md_file).replace('.md', '')
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Field Station Wiki</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #e6edf3;
            background-color: #0d1117;
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            background-color: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }}
        
        .header h1 {{
            margin: 0;
            color: #58a6ff;
        }}
        
        .nav {{
            background-color: #21262d;
            color: white;
            padding: 0.5rem 0;
            margin-bottom: 1rem;
            border-radius: 6px;
        }}
        
        .nav a {{
            color: #e6edf3;
            text-decoration: none;
            margin-right: 1rem;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            display: inline-block;
            transition: background-color 0.2s;
        }}
        
        .nav a:hover {{
            background-color: #30363d;
            color: #58a6ff;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
            line-height: 1.25;
        }}
        
        h1 {{ color: #58a6ff; font-size: 2rem; }}
        h2 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 0.3rem; font-size: 1.5rem; }}
        h3 {{ color: #7d8590; font-size: 1.25rem; }}
        h4 {{ color: #7d8590; font-size: 1rem; }}
        
        p {{
            margin-bottom: 1rem;
        }}
        
        code {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            font-size: 85%;
            margin: 0;
            padding: 0.2em 0.4em;
            font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
            color: #ffa657;
        }}
        
        pre {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            font-size: 85%;
            line-height: 1.45;
            overflow: auto;
            padding: 16px;
            margin: 1rem 0;
        }}
        
        pre code {{
            background-color: transparent;
            border: 0;
            display: inline;
            line-height: inherit;
            margin: 0;
            overflow: visible;
            padding: 0;
            word-wrap: normal;
            color: #e6edf3;
        }}
        
        ul, ol {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        a {{
            color: #58a6ff;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
            color: #79c0ff;
        }}
        
        strong {{
            color: #f0f6fc;
        }}
        
        em {{
            color: #f0f6fc;
            font-style: italic;
        }}
        
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #30363d;
            color: #7d8590;
            font-size: 0.9rem;
        }}
        
        .file-list {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        .file-list h3 {{
            margin-top: 0;
            color: #58a6ff;
        }}
        
        .file-list ul {{
            margin-bottom: 0;
        }}
        
        /* Dark mode scrollbar */
        ::-webkit-scrollbar {{
            width: 12px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #161b22;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #30363d;
            border-radius: 6px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #484f58;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🎮 Field Station Wiki</h1>
        </div>
    </div>
    
    <div class="nav">
        <div class="container">
            <a href="/WIKI_HOME">🏠 Home</a>
            <a href="/README">📖 README</a>
            <a href="/DEVELOPMENT_ROADMAP">🚀 Roadmap</a>
            <a href="/QA_README">🧪 QA Guide</a>
            <a href="/UI_DESIGN_PLAN">🎨 UI Design</a>
            <a href="/GAME_STRATEGY">🎯 Game Strategy</a>
            <a href="/SDLC_QA_README">📋 SDLC QA</a>
            <a href="/USER_STORIES">📚 User Stories</a>
        </div>
    </div>
    
    <div class="container">
        <div class="content">
            {content}
        </div>
        
        <div class="footer">
            <p>📝 <strong>Source:</strong> {md_file} | <strong>Field Station Project Wiki</strong></p>
            <p>💡 <strong>Tip:</strong> All markdown files are clickable links in the content above!</p>
        </div>
    </div>
</body>
</html>
        """

def main():
    """Start the simple wiki server"""
    PORT = 8082
    
    # Check if we're in the right directory
    if not os.path.exists('WIKI_HOME.md'):
        print("❌ WIKI_HOME.md not found. Please run from the field_station directory.")
        sys.exit(1)
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), SimpleWikiHandler) as httpd:
            print(f"🚀 Starting Field Station Wiki Server on port {PORT}")
            print(f"📖 Wiki URL: http://localhost:{PORT}")
            print(f"🏠 Home Page: http://localhost:{PORT}/WIKI_HOME")
            print("\n🌐 Opening in browser...")
            
            # Try to open in browser
            webbrowser.open(f'http://localhost:{PORT}')
            
            print(f"\n✅ Server running! Press Ctrl+C to stop.")
            print(f"📚 Available pages:")
            
            # List available markdown files
            md_files = sorted([f for f in os.listdir('.') if f.endswith('.md')])
            for md_file in md_files:
                print(f"  • http://localhost:{PORT}/{md_file}")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use. Try a different port.")
            print(f"💡 Or kill the existing server: lsof -ti:{PORT} | xargs kill")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()