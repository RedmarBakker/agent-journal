from journal.config import Config
from journal.db.connection import Connection
from journal.http.router import Router
from journal.http.server import Server
from journal.support.listener_queue import ListenerQueue


class SuiteServer:
    """The server as a test calls it over HTTP: once a request is answered, the work it left for after the answer has run before the test reads."""

    def __init__(self, server: Server, deferred: ListenerQueue) -> None:
        self.server, self.deferred = server, deferred
        self.config: Config = server.config
        self.database: Connection = server.database
        self.router: Router = server.router

    @property
    def port(self) -> int:
        return self.server.port

    def start(self) -> None:
        self.server.start()

    def stop(self) -> None:
        self.server.stop()

    def drain_queue(self) -> None:
        self.deferred.drain()
