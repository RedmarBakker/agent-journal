import hmac
import json
from http.server import BaseHTTPRequestHandler


class CapEventHandler(BaseHTTPRequestHandler):
    """Validate a local hook token before applying a live run cap event."""

    def __init__(self, *args, cap_server, **kwargs) -> None:
        self.cap_server = cap_server
        super().__init__(*args, **kwargs)

    def do_POST(self) -> None:
        if self.path != "/event" or not hmac.compare_digest(self.headers.get("X-Run-Cap-Token", ""), self.cap_server.token):
            self.send_error(403)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            event = json.loads(self.rfile.read(length))
            self.cap_server.accept(event)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self.send_error(409, str(error))
            return
        self.send_response(200)
        self.end_headers()

    def log_message(self, _format, *_args) -> None:
        return
