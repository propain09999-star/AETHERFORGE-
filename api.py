#!/usr/bin/env python3
"""AETHORFORGE API — connects Glass Cockpit UI to modules"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from http.server import HTTPServer, BaseHTTPRequestHandler
from code.grit.models import _groq_call

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = json.loads(self.rfile.read(length))
        query  = body.get('query', '')
        mode   = body.get('mode', 'bounty')
def do_GET(self):
        if self.path == "/telemetry":
            from code.shared.telemetry import get_telemetry
            data = get_telemetry()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()
        prompts = {
            'bounty':  f"Bug bounty expert. Recon plan for: {query}",
            'pentest': f"Senior pentester. Attack surface for: {query}",
            'forge':   f"Senior engineer. Generate code for: {query}",
            'domain':  f"Domain analyst. Answer: {query}",
        }
        prompt = prompts.get(mode, query)
        result = _groq_call(prompt, "llama-3.3-70b-versatile")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"result": result}).encode())

if __name__ == "__main__":
    port = 8000
    print(f"✓ AETHORFORGE API running on http://localhost:{port}")
    print(f"  Open ui/index.html in browser")
    print(f"  Ctrl+C to stop")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
