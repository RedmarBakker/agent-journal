import select
import socket
import tempfile
import threading
from pathlib import Path

from supervisor.inbox import Inbox
from supervisor.reply import Reply
from supervisor.request import Request


class StorySupervisor:
    """A supervisor inbox that records accepted terminal lines without starting an agent."""

    def __init__(self, home: Path, environment: str, lines: list[str]) -> None:
        self.folder = tempfile.TemporaryDirectory(prefix="journal-story-", dir="/tmp")
        self.inbox = Inbox(Path(self.folder.name) / "s.sock", home / "runtime" / "inboxes" / environment)
        self.inbox.open()
        self.environment = environment
        self.lines = lines
        self.accepted: list[str] = []
        self.refusal = ""
        self.wake, self.woken = socket.socketpair()
        self.thread = threading.Thread(target=self.answer, name="story-supervisor", daemon=True)
        self.thread.start()

    def answer(self) -> None:
        while self.woken not in select.select((self.inbox.fd, self.woken), (), ())[0]:
            self.inbox.answer(self.handle)

    def handle(self, request: Request) -> Reply:
        if self.refusal:
            return Reply.refused(self.refusal)
        if request.verb == "type":
            self.accepted.append(request.line)
            self.lines.append(request.line)
        return Reply.success()

    def refuse(self) -> None:
        self.refusal = "the agent terminal is not ready"

    def accept(self) -> None:
        self.refusal = ""

    def close(self) -> None:
        self.wake.sendall(b"x")
        self.thread.join(5)
        assert not self.thread.is_alive(), "the story supervisor did not stop"
        self.inbox.close()
        self.wake.close()
        self.woken.close()
        self.folder.cleanup()
