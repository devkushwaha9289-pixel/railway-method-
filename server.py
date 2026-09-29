import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

PORT = int(os.environ.get("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_json({
                "success": True,
                "message": "Railway serverless service is running",
                "status": "online"
            })

        elif self.path == "/health":
            self.send_json({
                "success": True,
                "status": "healthy"
            })

        else:
            self.send_json({
                "success": False,
                "error": "Endpoint not found"
            }, 404)

    def log_message(self, format, *args):
        print(format % args)


server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

print(f"Server running on port {PORT}")

server.serve_forever()
