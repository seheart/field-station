#!/usr/bin/env python3
"""
Field Station Wiki Server
Serves markdown files as HTML in Chrome browser
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path
import markdown
import re
from urllib.parse import unquote

class WikiHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving markdown as HTML"""
    
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
        """Convert markdown to HTML and serve it"""
        try:
            if not os.path.exists(md_file):
                self.send_error(404, f"File not found: {md_file}")
                return
            
            # Read markdown content
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['tables', 'codehilite', 'toc'])
            html_content = md.convert(md_content)
            
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
    
    def create_html_page(self, content, md_file):
        """Create a complete HTML page with styling"""
        # Convert local markdown links to work in browser
        content = re.sub(r'\[([^\]]+)\]\(([^)]+\.md)\)', r'<a href="/\2">\1</a>', content)
        
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
            color: #24292f;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            background-color: #f6f8fa;
            border-bottom: 1px solid #d1d9e0;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }}
        
        .header h1 {{
            margin: 0;
            color: #0969da;
        }}
        
        .nav {{
            background-color: #0969da;
            color: white;
            padding: 0.5rem 0;
            margin-bottom: 1rem;
        }}
        
        .nav a {{
            color: white;
            text-decoration: none;
            margin-right: 1rem;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
        }}
        
        .nav a:hover {{
            background-color: rgba(255,255,255,0.1);
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
            line-height: 1.25;
        }}
        
        h1 {{ color: #0969da; }}
        h2 {{ color: #0969da; border-bottom: 1px solid #d1d9e0; padding-bottom: 0.3rem; }}
        h3 {{ color: #656d76; }}
        
        code {{
            background-color: #f6f8fa;
            border-radius: 6px;
            font-size: 85%;
            margin: 0;
            padding: 0.2em 0.4em;
        }}
        
        pre {{
            background-color: #f6f8fa;
            border-radius: 6px;
            font-size: 85%;
            line-height: 1.45;
            overflow: auto;
            padding: 16px;
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
        }}
        
        table {{
            border-collapse: collapse;
            border-spacing: 0;
            width: 100%;
            margin: 1rem 0;
        }}
        
        table th, table td {{
            border: 1px solid #d1d9e0;
            padding: 6px 13px;
        }}
        
        table th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        blockquote {{
            border-left: 0.25em solid #d1d9e0;
            color: #656d76;
            margin: 0;
            padding: 0 1em;
        }}
        
        a {{
            color: #0969da;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .emoji {{
            font-style: normal;
        }}
        
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #d1d9e0;
            color: #656d76;
            font-size: 0.9rem;
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
        </div>
    </div>
    
    <div class="container">
        <div class="content">
            {content}
        </div>
        
        <div class="footer">
            <p>📝 <strong>Source:</strong> {md_file} | <strong>Field Station Project Wiki</strong></p>
        </div>
    </div>
</body>
</html>
        """

def main():
    """Start the wiki server"""
    PORT = 8080
    
    # Check if we're in the right directory
    if not os.path.exists('WIKI_HOME.md'):
        print("❌ WIKI_HOME.md not found. Please run from the field_station directory.")
        sys.exit(1)
    
    # Install markdown if not available
    try:
        import markdown
    except ImportError:
        print("📦 Installing markdown library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), WikiHandler) as httpd:
            print(f"🚀 Starting Field Station Wiki Server on port {PORT}")
            print(f"📖 Wiki URL: http://localhost:{PORT}")
            print(f"🏠 Home Page: http://localhost:{PORT}/WIKI_HOME")
            print("\n🌐 Opening in Chrome...")
            
            # Try to open in Chrome specifically
            chrome_paths = [
                'google-chrome',
                'chromium-browser', 
                'chromium',
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser',
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            ]
            
            chrome_opened = False
            for chrome_path in chrome_paths:
                try:
                    import subprocess
                    subprocess.Popen([chrome_path, f'http://localhost:{PORT}'], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    chrome_opened = True
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            
            if not chrome_opened:
                # Fallback to default browser
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