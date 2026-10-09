import http.server
import socketserver
import json
import glob
import os
from validate import validate_fighter

PORT = int(os.environ.get("PORT", 3000))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/fighters':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}
                
            fighters = []
            for filepath in glob.glob("fighters/*.json"):
                if os.path.basename(filepath).startswith("_"):
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    problems = validate_fighter(content, config)
                    if not any(p["severity"] == "error" for p in problems):
                        fighter = json.loads(content)
                        fighters.append(fighter)
                except Exception:
                    pass
                    
            self.wfile.write(json.dumps(fighters).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving at http://0.0.0.0:{PORT}", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
