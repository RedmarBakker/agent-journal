import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler

from sync_server.json_reply import JsonReply


class EventRequestHandler(BaseHTTPRequestHandler):
    """One event the journal server posts to the sync service, handed to its carrier, whose answer goes back as the reply; and the service's health, 200 while its loops live."""

    def do_GET(self) -> None:
        if self.path != "/health":
            JsonReply.send(self, 404, {"error": f"no {self.path} here"})
            return
        JsonReply.send(self, 200 if self.server.carrier.is_working() else 503, {"working": self.server.carrier.is_working()})

    def do_POST(self) -> None:
        event = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            JsonReply.send(self, 200, self.server.carrier.reply(str(event.get("event", ""))))
        except Exception as fault:
            sys.stderr.write(f"the sync service could not take {event.get('event')}:\n{traceback.format_exc()}")
            JsonReply.send(self, 500, {"error": f"{type(fault).__name__}: {fault}"})

    def log_message(self, format: str, *args) -> None:
        return
