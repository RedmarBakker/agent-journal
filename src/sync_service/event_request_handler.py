import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler


class EventRequestHandler(BaseHTTPRequestHandler):
    """One event the journal server posts to the sync service, handed to its carrier, whose answer goes back as the reply."""

    def do_POST(self) -> None:
        event = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            self.answered(200, self.server.carrier.heard(event))
        except Exception as fault:
            sys.stderr.write(f"the sync service could not take {event.get('event')}:\n{traceback.format_exc()}")
            self.answered(500, {"error": f"{type(fault).__name__}: {fault}"})

    def answered(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return
