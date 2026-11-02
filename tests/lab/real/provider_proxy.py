import select
import socket
import socketserver
from threading import Event, Thread

from tests.lab.real.provider_proxy_handler import ProviderProxyHandler


PROVIDER_HOSTS = frozenset({
    "api.anthropic.com", "auth.anthropic.com", "claude.ai", "console.anthropic.com",
    "api.openai.com", "auth.openai.com", "chatgpt.com",
})


class ProviderProxy:
    """Proxy provider HTTPS traffic while denying other network destinations."""

    def __init__(self, port: int = 0) -> None:
        self.stopped = Event()
        self.server = socketserver.ThreadingTCPServer(("127.0.0.1", port), ProviderProxyHandler)
        self.server.owner = self
        self.server.daemon_threads = True
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return self.server.server_address[1]

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.stopped.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    @staticmethod
    def allowed(host: str) -> bool:
        lowered = host.rstrip(".").lower()
        return lowered in PROVIDER_HOSTS

    def relay(self, client: socket.socket, upstream: socket.socket) -> None:
        while not self.stopped.is_set():
            ready, _, _ = select.select((client, upstream), (), (), 0.25)
            for source in ready:
                data = source.recv(65536)
                if not data:
                    return
                (upstream if source is client else client).sendall(data)
