from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread

from tests.lab.real.cap_event_handler import CapEventHandler


class CapEventServer:
    """Admit provider sessions and turns before the provider receives them."""

    def __init__(self, caps, token: str, port: int = 0) -> None:
        self.caps, self.token = caps, token
        self.server = ThreadingHTTPServer(("127.0.0.1", port), partial(CapEventHandler, cap_server=self))
        self.server.daemon_threads = True
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> int:
        self.thread.start()
        return self.server.server_address[1]

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def accept(self, event: object) -> None:
        if not isinstance(event, dict):
            raise ValueError("provider cap event must be an object")
        kind, session_id = event.get("event"), event.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("provider cap event needs a session id")
        if kind == "SessionStart":
            self.caps.start_session(session_id)
        elif kind == "UserPromptSubmit":
            firing = event.get("firing")
            if not isinstance(firing, str) or not firing:
                raise ValueError("provider turn event needs a unique hook firing")
            self.caps.reserve_request(f"{session_id}:{firing}", session_id)
        elif kind == "SessionEnd":
            self.caps.finish_session(session_id)
        else:
            raise ValueError("provider cap event type is not supported")

