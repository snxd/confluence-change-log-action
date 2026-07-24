"""
A lightweight mock Confluence REST API server for testing the GitHub action
end-to-end without a real Confluence instance.

Implements just enough of the Confluence API to support:
  - GET /wiki/rest/api/space/{key}                     (get space id)
  - GET /wiki/api/v2/pages/{id}                         (get current version)
  - GET /wiki/rest/api/content/{id}?expand=body.storage (get existing content)
  - PUT /wiki/api/v2/pages/{id}                         (update the page)
"""

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

SPACE_KEY = "TEST"
SPACE_ID = "393217"
PAGE_ID = "123456"

# In-memory page store keyed by page id
pages = {
    PAGE_ID: {
        "id": PAGE_ID,
        "status": "current",
        "title": "Test Change Log",
        "spaceId": SPACE_ID,
        "version": {"number": 1},
        "body": {"storage": {"value": "<p>Existing content</p>", "representation": "storage"}},
    }
}


class ConfluenceHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, message):
        self._send_json({"statusCode": status, "message": message}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        parts = self.path.split("?")[0].rstrip("/").split("/")

        # GET /wiki/rest/api/space/{key}
        if self.path.startswith("/wiki/rest/api/space/"):
            key = parts[-1]
            if key == SPACE_KEY:
                self._send_json({"id": SPACE_ID, "key": SPACE_KEY})
            else:
                self._send_error(404, f"No space found with key : {key}")
            return

        # GET /wiki/rest/api/content/{id}?expand=body.storage
        if self.path.startswith("/wiki/rest/api/content/"):
            page = pages.get(parts[-1])
            if page:
                self._send_json({"id": page["id"], "body": page["body"]})
            else:
                self._send_error(404, "Page not found")
            return

        # GET /wiki/api/v2/pages/{id}
        if self.path.startswith("/wiki/api/v2/pages/"):
            page = pages.get(parts[-1])
            if page:
                self._send_json(page)
            else:
                self._send_error(404, "Page not found")
            return

        self._send_error(404, "Not found")

    def do_PUT(self):
        # PUT /wiki/api/v2/pages/{id}
        if self.path.startswith("/wiki/api/v2/pages/"):
            page_id = self.path.rstrip("/").split("/")[-1]
            page = pages.get(page_id)
            if not page:
                self._send_error(404, "Page not found")
                return

            data = self._read_body()
            page["version"]["number"] = data.get("version", {}).get("number", page["version"]["number"])
            page["title"] = data.get("title", page["title"])
            page["status"] = data.get("status", page["status"])
            if "body" in data:
                page["body"]["storage"]["value"] = data["body"].get("value", "")
            self._send_json(page)
            return

        self._send_error(404, "Not found")

    # Suppress request logging to keep CI output clean
    def log_message(self, format, *args):
        print(f"[mock-confluence] {args[0]}")


def main():
    parser = argparse.ArgumentParser(description="Mock Confluence API server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--space-key", default="TEST")
    parser.add_argument("--page-id", default="123456")
    args = parser.parse_args()

    global SPACE_KEY, PAGE_ID
    SPACE_KEY = args.space_key
    PAGE_ID = args.page_id
    pages[PAGE_ID] = pages.pop(next(iter(pages)))
    pages[PAGE_ID]["id"] = PAGE_ID

    server = HTTPServer(("0.0.0.0", args.port), ConfluenceHandler)
    print(f"Mock Confluence server listening on port {args.port} (space: {SPACE_KEY}, page: {PAGE_ID})")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
