import threading
from http.server import ThreadingHTTPServer

from sync_service.event_request_handler import EventRequestHandler


class EventInbox:
    """Where the journal server posts the sync service the events it registered for, and where its health is asked: a server on the loopback port given, or a free one, each post answered by the carrier."""

    def __init__(self, carrier, port: int = 0) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", port), EventRequestHandler)
        self.server.daemon_threads = True
        self.server.carrier = carrier

    @property
    def address(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}/events"

    def start(self) -> None:
        threading.Thread(target=self.server.serve_forever, name="sync events", daemon=True).start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
