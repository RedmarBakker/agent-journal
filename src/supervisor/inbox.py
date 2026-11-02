import json
import socket
import stat
from collections.abc import Callable
from pathlib import Path

from supervisor.reply import Reply
from supervisor.request import Request

LONGEST = 1 << 20
PROTOCOL = 1
WAIT_SECONDS = 2.0


class Inbox:
    """A Unix socket the journal asks through, one per supervisor: private sockets belong to their user, while a shared setgid folder gives its group access to one socket."""

    def __init__(self, path: Path, announced_at: Path, shared_group: int | None = None) -> None:
        self.path, self.announced_at, self.shared_group = path, announced_at, shared_group
        self._socket: socket.socket | None = None

    @property
    def fd(self) -> int:
        return self._socket.fileno()

    def open(self) -> None:
        self.announce({})

    def open_mirrored(self, screen: Path) -> None:
        self.announce({"screen": str(screen)})

    def announce(self, fields: dict[str, str]) -> None:
        if self.shared_group is None:
            self.path.parent.mkdir(mode=0o700, exist_ok=True)
            self.path.parent.chmod(0o700)
        else:
            self.shared_folder()
        self.path.unlink(missing_ok=True)
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.bind(str(self.path))
        self.path.chmod(0o660 if self.shared_group is not None else 0o600)
        if self.shared_group is not None and self.path.stat().st_gid != self.shared_group:
            self.close()
            raise PermissionError("the Plan supervisor socket did not inherit its shared group")
        self._socket.listen(8)
        self._socket.setblocking(False)
        self.announced_at.parent.mkdir(parents=True, exist_ok=True)
        self.announced_at.write_text(json.dumps({"socket": str(self.path), "protocol": PROTOCOL, **fields}))

    def shared_folder(self) -> None:
        folder = self.path.parent.stat()
        if folder.st_gid != self.shared_group or stat.S_IMODE(folder.st_mode) != 0o2770:
            raise PermissionError("the shared supervisor socket folder must have its configured group and mode 2770")

    def answer(self, handle: Callable[[Request], Reply]) -> None:
        while True:
            try:
                connection, _ = self._socket.accept()
            except BlockingIOError:
                return
            with connection:
                connection.settimeout(WAIT_SECONDS)
                reply = self.handled(connection, handle)
                try:
                    connection.sendall((json.dumps(reply.as_json()) + "\n").encode())
                except OSError:
                    continue

    @staticmethod
    def handled(connection: socket.socket, handle: Callable[[Request], Reply]) -> Reply:
        try:
            payload = json.loads(connection.makefile("rb").readline(LONGEST))
        except (ValueError, OSError) as fault:
            return Reply.refused(f"the request is no line of JSON: {fault}")
        if not isinstance(payload, dict):
            return Reply.refused("the request is no JSON object")
        return handle(Request.parsed(payload))

    def close(self) -> None:
        if self._socket:
            self._socket.close()
        self.path.unlink(missing_ok=True)
        self.announced_at.unlink(missing_ok=True)
