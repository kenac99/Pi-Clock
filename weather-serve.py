#!/usr/bin/env python3
"""Serves weather.json on port 8090 and handles chain toggle via POST /chain."""
import http.server, json, os

PORT = 8090
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAIN_FILE = os.path.join(SCRIPT_DIR, "chain.txt")
CHAINS = ["btc", "bch"]

os.chdir(SCRIPT_DIR)


def read_chain():
    try:
        return open(CHAIN_FILE).read().strip().lower()
    except Exception:
        return "btc"


def write_chain(c):
    with open(CHAIN_FILE, "w") as f:
        f.write(c)


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/chain":
            body = json.dumps({"chain": read_chain()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/weather.json"):
            weather_path = os.path.join(SCRIPT_DIR, "weather.json")
            try:
                with open(weather_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_response(404)
                self.end_headers()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/chain":
            current = read_chain()
            nxt = CHAINS[(CHAINS.index(current) + 1) % len(CHAINS)] if current in CHAINS else "btc"
            write_chain(nxt)
            body = json.dumps({"chain": nxt}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/clear-block":
            weather_path = os.path.join(SCRIPT_DIR, "weather.json")
            try:
                with open(weather_path) as f:
                    data = json.load(f)
                data.pop("block_chain", None)
                with open(weather_path, "w") as f:
                    json.dump(data, f)
                body = json.dumps({"ok": True}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
