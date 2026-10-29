import json
from dataclasses import replace
from pathlib import Path
from threading import Lock

from journal.providers.support.agent_status import AgentStatus
from journal.providers.support.codex_status_update import CodexStatusUpdate

UNREPORTED = AgentStatus("", "", None, ())


class CodexStatusFile:
    """The latest status a Codex session's rollout reports, read from its complete records as they are appended, from the start again when the file is replaced or cut short: the model and effort of its last turn, and how full its context is from the last request's tokens against the model's window."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.read_bytes = 0
        self.identity: tuple[int, int] | None = None
        self.context_tokens: int | None = None
        self.current = UNREPORTED
        self.lock = Lock()

    def reading(self) -> AgentStatus:
        with self.lock:
            self.restarted_if_replaced()
            for record in self.new_records():
                self.recorded(CodexStatusUpdate.parsed(record))
            return self.current

    def restarted_if_replaced(self) -> None:
        stat = self.path.stat()
        identity = (stat.st_dev, stat.st_ino)
        if identity != self.identity or stat.st_size < self.read_bytes:
            self.read_bytes, self.context_tokens, self.current, self.identity = 0, None, UNREPORTED, identity

    def new_records(self) -> list[dict]:
        with self.path.open("rb") as file:
            file.seek(self.read_bytes)
            appended = file.read()
        complete = appended.rfind(b"\n") + 1
        self.read_bytes += complete
        return [json.loads(line) for line in appended[:complete].splitlines() if line.strip()]

    def recorded(self, update: CodexStatusUpdate) -> None:
        if update.model is not None:
            self.current = replace(self.current, model=update.model)
        if update.effort is not None:
            self.current = replace(self.current, effort=update.effort)
        if isinstance(update.context_tokens, int) and update.context_tokens > 0:
            self.context_tokens = update.context_tokens
        if isinstance(update.used_tokens, int) and self.context_tokens is not None:
            self.current = replace(self.current, context=min(1.0, max(0.0, update.used_tokens / self.context_tokens)))
