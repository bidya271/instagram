"""
server.py — Local Web API server on port 7777
Zero external dependencies (stdlib only).
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json, mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from quarky import db
from quarky.strategist import generate_blueprint, list_blueprints, load_blueprint
from quarky.scout import run_scout
from quarky.writer import run_draft
from quarky.pusher import push_outbox_item, reject_outbox_item

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
PORT = 7777

class QuarkyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence default logging

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        db.init_db()

        # ── Static files ─────────────────────────────────────
        if path == "/" or path == "/index.html":
            self._serve_file(os.path.join(WEB_DIR, "index.html"))
            return
        if path in ("/style.css", "/app.js"):
            self._serve_file(os.path.join(WEB_DIR, path.lstrip("/")))
            return

        # ── API ───────────────────────────────────────────────
        if path == "/api/profiles":
            self._json(list_blueprints())
        elif path == "/api/outbox":
            app = qs.get("app", [None])[0]
            status = qs.get("status", ["pending_approval"])[0]
            self._json(db.get_outbox(target_app=app, status=status))
        elif path == "/api/leads":
            app = qs.get("app", [None])[0]
            self._json(db.get_leads(target_app=app))
        elif path == "/api/stats":
            self._json(db.get_stats())
        else:
            self._json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        db.init_db()

        if path == "/api/analyze":
            product_input = body.get("product", "")
            slug = body.get("slug", "").strip().replace(" ", "_").lower() or None
            if not product_input:
                self._json({"error": "product required"}, 400)
                return
            blueprint = generate_blueprint(product_input, slug)
            self._json(blueprint)

        elif path == "/api/scout":
            app_slug = body.get("app_slug", "")
            if not app_slug:
                self._json({"error": "app_slug required"}, 400)
                return
            count = run_scout(app_slug, verbose=True)
            self._json({"new_leads": count})

        elif path == "/api/draft":
            app_slug = body.get("app_slug", "")
            if not app_slug:
                self._json({"error": "app_slug required"}, 400)
                return
            count = run_draft(app_slug, verbose=True)
            self._json({"drafted": count})

        elif path == "/api/push":
            outbox_id = body.get("outbox_id")
            pitch_text = body.get("pitch_text")
            if outbox_id is None:
                self._json({"error": "outbox_id required"}, 400)
                return
            result = push_outbox_item(int(outbox_id), pitch_text)
            self._json(result)

        elif path == "/api/reject":
            outbox_id = body.get("outbox_id")
            if outbox_id is None:
                self._json({"error": "outbox_id required"}, 400)
                return
            result = reject_outbox_item(int(outbox_id))
            self._json(result)

        else:
            self._json({"error": "Not found"}, 404)

    def _serve_file(self, filepath):
        if not os.path.exists(filepath):
            self._json({"error": "File not found"}, 404)
            return
        mime, _ = mimetypes.guess_type(filepath)
        mime = mime or "application/octet-stream"
        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

def run():
    db.init_db()
    httpd = HTTPServer(("127.0.0.1", PORT), QuarkyHandler)
    print(f"🚀 Quarky running at http://localhost:{PORT}")
    print(f"   Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Quarky stopped.")

if __name__ == "__main__":
    run()
