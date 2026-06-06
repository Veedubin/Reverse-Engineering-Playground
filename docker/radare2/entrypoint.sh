#!/bin/sh
# RE_Playground radare2 entrypoint
# Runs r2mcp (stdio) and also serves a tiny HTTP health endpoint on R2MCP_PORT
# so the orchestrator (and Docker HEALTHCHECK) can verify liveness.

set -e

R2MCP_PORT="${R2MCP_PORT:-9090}"

# Background HTTP health server — single-thread, no deps
python3 - <<EOF &
import http.server, socketserver, sys
class Health(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok","r2mcp":"running"}')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *args, **kwargs):
        pass  # quiet
with socketserver.TCPServer(("0.0.0.0", ${R2MCP_PORT}), Health) as srv:
    srv.serve_forever()
EOF

HEALTH_PID=$!
echo "radare2 health server on :${R2MCP_PORT} (pid ${HEALTH_PID})"

# Start r2mcp in foreground (this is the actual MCP server)
if command -v r2mcp >/dev/null 2>&1; then
    exec r2mcp
elif command -v r2pm >/dev/null 2>&1; then
    exec r2pm -r r2mcp
else
    echo "ERROR: r2mcp not found in PATH" >&2
    exit 1
fi
