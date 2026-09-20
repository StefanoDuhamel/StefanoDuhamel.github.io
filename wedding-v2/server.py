#!/usr/bin/env python3
"""Serve the new wedding design and save RSVPs locally.

Run from this folder with: python3 server.py
Then open http://localhost:8788
"""
import json
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RSVP_FILE = HERE / "rsvps.json"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/wedding-v2/index.html"
        super().do_GET()

    def do_POST(self):
        if self.path != "/rsvp":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(size) or b"{}")
            record = {"received_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **data}
            with RSVP_FILE.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_error(400, str(error))

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    #server = ThreadingHTTPServer(("127.0.0.1", 8788), Handler)
    server = ThreadingHTTPServer(("0.0.0.0", 8788), Handler)
    print("Serving the new wedding site at http://localhost:8788")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
