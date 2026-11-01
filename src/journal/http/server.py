import ssl
import threading

from journal.config import Config
from journal.db.connection import Connection
from journal.engine.lifecycle import Lifecycle
from journal.http.handler import Handler
from journal.http.supervisor_handler import SupervisorHandler
from journal.http.support.identity import Identity
from journal.http.support.request_faults import RequestFaults
from journal.support.fault_log import FaultLog
from journal.http.router import Router
from journal.http.static_files import StaticFiles
from journal.http.threading_server import ThreadingServer
from journal.sync.sync_secret import SyncSecret
from journal.http.support.supervisor_authentication import SupervisorRequestAuth


class Server:
    """One process owns the journal's primary and optional private listeners; it records the primary port for hooks and removes it only while it still owns that value."""

    def __init__(self, config: Config, router: Router, identity: Identity, static: StaticFiles, database: Connection, lifecycle: Lifecycle, secret: SyncSecret, faults: RequestFaults, fault_log: FaultLog, supervisor_auth: SupervisorRequestAuth) -> None:
        self.config, self.router, self.identity, self.static, self.database, self.lifecycle = config, router, identity, static, database, lifecycle
        self.faults, self.fault_log = faults, fault_log
        self.secret = secret
        self.supervisor_auth = supervisor_auth
        self._bound: list[ThreadingServer] = []
        self._threads: list[threading.Thread] = []
        self._thread = threading.Thread(target=lambda: self._bound[0].serve_requests(), name="http", daemon=True)

    @property
    def port(self) -> int:
        return self._bound[0].server_address[1]

    def start(self) -> None:
        bound = [self._build()]
        names = ["http"]
        try:
            if self.config.owner_access_listener is not None:
                bound.append(self._build_owner_access())
                names.append("owner-access-http")
            if self.config.supervisor_listener is not None:
                bound.append(self._build_supervisor())
                names.append("supervisor-http")
        except Exception:
            for server in bound:
                server.server_close()
            raise
        self._bound.extend(bound)
        self._threads = [self._thread]
        for server, name in zip(bound[1:], names[1:]):
            self._threads.append(threading.Thread(target=lambda service=server: service.serve_requests(), name=name, daemon=True))
        self.config.home.mkdir(parents=True, exist_ok=True)
        self.config.port_file.write_text(str(self.port))
        self.secret.issued()
        for thread in self._threads:
            thread.start()

    def serve(self) -> None:
        self.start()
        self._thread.join()

    def stop(self) -> None:
        for server, thread in zip(self._bound, self._threads):
            if thread.is_alive():
                server.shutdown()
        for thread in self._threads:
            if thread.ident is not None:
                thread.join()
        for bound in self._bound:
            bound.server_close()
        if self._bound and self.is_port_file_owned():
            self.config.port_file.unlink(missing_ok=True)

    def is_port_file_owned(self) -> bool:
        return self.config.port_file.is_file() and self.config.port_file.read_text().strip() == str(self.port)

    def _build(self) -> ThreadingServer:
        return self._bind(self._handler(Handler))

    def _build_supervisor_handler(self) -> type[SupervisorHandler]:
        return self._handler(SupervisorHandler)

    def _build_owner_access(self) -> ThreadingServer:
        host, port = self.config.owner_access_listener
        return ThreadingServer((host, port), self._handler(Handler))

    def _build_supervisor(self) -> ThreadingServer:
        host, port, certificate, key = self.config.supervisor_listener
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certificate, key)
        server = ThreadingServer((host, port), self._build_supervisor_handler())
        try:
            server.socket = context.wrap_socket(server.socket, server_side=True)
        except Exception:
            server.server_close()
            raise
        return server

    def _handler(self, base: type[Handler]) -> type[Handler]:
        return type("BoundHandler", (base,), {"router": self.router, "identity": self.identity, "static": self.static, "database": self.database, "lifecycle": self.lifecycle, "faults": self.faults, "fault_log": self.fault_log, "supervisor_auth": self.supervisor_auth})

    def _bind(self, handler: type[Handler]) -> ThreadingServer:
        ports = self.config.ports()
        for port in ports[:-1]:
            try:
                return ThreadingServer((self.config.host, port), handler)
            except OSError:
                continue
        return ThreadingServer((self.config.host, ports[-1]), handler)
