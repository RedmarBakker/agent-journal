import os
import signal
import subprocess
import threading
import time
from pathlib import Path

from supervisor.health_check import HealthCheck

BACKOFF = 2.0
LONGEST_WAIT_SECONDS = 30.0
WINDOW_SECONDS = 120.0
STOP_GRACE = 5.0


class Service:
    """A named process beside the agent, with no terminal: what is sent to it goes to its input, its output goes to its log, and it is started again when it dies or, when it names a health check, when it fails that check too many times in a row."""

    def __init__(self, name: str, command: list[str], folder: Path, environ: dict[str, str], log: Path, persistent: bool = True, health: HealthCheck | None = None) -> None:
        self.name, self.command, self.folder, self.environ, self.log, self.persistent = name, command, folder, environ, log, persistent
        self.health = health
        self._failures = 0
        self._checked_at = 0.0
        self._process: subprocess.Popen | None = None
        self._last_start = 0.0
        self._deaths: list[float] = []
        self._restarts = 0
        self._moving = threading.RLock()

    def start(self) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self._last_start = time.time()
        with self.log.open("ab") as log_file:
            try:
                self._process = subprocess.Popen(self.command, cwd=self.folder, env=self.environ, stdin=subprocess.PIPE, stdout=log_file, stderr=log_file, start_new_session=True)
            except OSError as fault:
                log_file.write(f"{self.name} could not start: {fault}\n".encode())
                self._deaths = [death for death in self._deaths if self._last_start - death < WINDOW_SECONDS] + [self._last_start]

    def restart(self) -> None:
        with self._moving:
            self.stop()
            self.start()

    # the line that says why the service was started again when it failed its health check too many times in a row, else none
    def health_restart(self) -> str:
        moment = time.time()
        if self.health is None or not self.is_active() or moment - self._last_start < self.health.grace_seconds or moment - self._checked_at < self.health.interval_seconds:
            return ""
        self._checked_at = moment
        fault = self.health.fault()
        self._failures = self._failures + 1 if fault else 0
        if self._failures < self.health.failures:
            return ""
        self._failures = 0
        self._restarts += 1
        self.restart()
        return f"{self.name} failed its health check {self.health.failures} times in a row ({fault}): started again"

    def is_active(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def revive(self) -> None:
        if not self._moving.acquire(blocking=False):
            return
        try:
            self.revive_dead()
        finally:
            self._moving.release()

    def revive_dead(self) -> None:
        if self._process is None or self.is_active():
            return
        moment = time.time()
        if not self._deaths or self._deaths[-1] < self._last_start:
            self._deaths = [death for death in self._deaths if moment - death < WINDOW_SECONDS] + [moment]
        if not self.persistent:
            return
        wait = 0.0 if len(self._deaths) == 1 else min(BACKOFF * 2 ** (len(self._deaths) - 2), LONGEST_WAIT_SECONDS)
        if moment - self._deaths[-1] >= wait:
            self._restarts += 1
            self.start()

    def send(self, data: bytes) -> None:
        if not self.is_active():
            raise LookupError(f"{self.name} is not running")
        self._process.stdin.write(data)
        self._process.stdin.flush()

    def pid(self) -> int:
        return self._process.pid if self.is_active() else 0

    def described(self) -> dict:
        return {"name": self.name, "pid": self.pid(), "running": self.is_active(), "terminal": False, "front": False, "restarts": self._restarts}

    def stop(self) -> None:
        with self._moving:
            process = self._process
            if process is not None and process.poll() is None:
                self.signal_group(process, signal.SIGTERM)
                deadline = time.time() + STOP_GRACE
                while process.poll() is None and time.time() < deadline:
                    time.sleep(0.05)
                self.signal_group(process, signal.SIGKILL)
                process.wait()
            self._process = None

    @staticmethod
    def signal_group(process: subprocess.Popen, signal_kind: signal.Signals) -> None:
        try:
            os.killpg(process.pid, signal_kind)
        except (ProcessLookupError, PermissionError):
            return
