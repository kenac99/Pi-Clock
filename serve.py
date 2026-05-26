#!/usr/bin/env python3
import http.server, json, os

PORT = 8080
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

CONFIG_FILE  = os.path.join(BASE, 'config.json')
WEATHER_FILE = os.path.join(BASE, 'weather.json')

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == '/config':
            self.send_response(302)
            self.send_header('Location', '/config.html')
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/save-config':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                # Only allow known keys
                allowed = {'dayBright', 'nightBright', 'dayScheme', 'nightScheme', 'lat', 'lon'}
                clean = {k: v for k, v in data.items() if k in allowed}
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(clean, f)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"ok":false}')
        elif self.path == '/clear-block':
            try:
                with open(WEATHER_FILE) as f:
                    data = json.load(f)
                data.pop('block_chain', None)
                with open(WEATHER_FILE, 'w') as f:
                    json.dump(data, f)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
