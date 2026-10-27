import threading

from journal.config import Config
from journal.db.connection import Connection
from journal.engine.lifecycle import Lifecycle
from journal.http.handler import Handler
from journal.http.support.identity import Identity
from journal.http.support.login_gate import LoginGate
from journal.http.support.request_faults import RequestFaults
from journal.support.fault_log import FaultLog
from journal.http.router import Router
from journal.http.static_files import StaticFiles
from journal.http.threading_server import ThreadingServer
from journal.sync.sync_secret import SyncSecret


class Server:
    """One process, one port; every request is answered on a thread of its own. The port it got is written where the hook script reads it, and removed when it stops only while the file still names that port."""

    def __init__(self, config: Config, router: Router, identity: Identity, static: StaticFiles, database: Connection, gate: LoginGate, lifecycle: Lifecycle, secret: SyncSecret, faults: RequestFaults, fault_log: FaultLog) -> None:
        self.config, self.router, self.identity, self.static, self.database, self.gate, self.lifecycle = config, router, identity, static, database, gate, lifecycle
        self.faults, self.fault_log = faults, fault_log
        self.secret = secret
        self._bound: list[ThreadingServer] = []
        self._thread = threading.Thread(target=lambda: self._bound[0].serve_requests(), name="http", daemon=True)

    @property
    def port(self) -> int:
        return self._bound[0].server_address[1]

    def start(self) -> None:
        self._bound.append(self._build())
        self.config.home.mkdir(parents=True, exist_ok=True)
        self.config.port_file.write_text(str(self.port))
        self.secret.issued()
        self._thread.start()

    def serve(self) -> None:
        self.start()
        self._thread.join()

    def stop(self) -> None:
        if self._thread.is_alive():
            self._bound[0].shutdown()
        for bound in self._bound:
            bound.server_close()
        if self._bound and self.is_port_file_owned():
            self.config.port_file.unlink(missing_ok=True)

    def is_port_file_owned(self) -> bool:
        return self.config.port_file.is_file() and self.config.port_file.read_text().strip() == str(self.port)

    def _build(self) -> ThreadingServer:
        bound = type("BoundHandler", (Handler,), {"router": self.router, "identity": self.identity, "static": self.static, "database": self.database, "gate": self.gate, "lifecycle": self.lifecycle, "faults": self.faults, "fault_log": self.fault_log})
        return self._bind(bound)

    def _bind(self, handler: type[Handler]) -> ThreadingServer:
        ports = self.config.ports()
        for port in ports[:-1]:
            try:
                return ThreadingServer(("127.0.0.1", port), handler)
            except OSError:
                continue
        return ThreadingServer(("127.0.0.1", ports[-1]), handler)
