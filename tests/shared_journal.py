import os
import shutil
import sqlite3
from journal.support.agent_role import AgentRole
from pathlib import Path

from journal.app import App
from journal.db.connection import Connection
from journal.features.shell.support.shell_runner import ShellRunner
from journal.support.secret_values import SecretValues
from tests.service_memory import ServiceMemory
from sync_server.team_server import DATABASE as TEAM_DATABASE



class SharedJournal:
    """One booted journal for the tests of a module, put back after each test as it stood at boot: its rows and their numbering, the files under its root and its secret values, the services built since and what the services built at boot remember."""

    def __init__(self, app: App) -> None:
        self.app = app
        app.console().parser(AgentRole.MAIN)
        self.settled()
        self.rows = sqlite3.connect(":memory:")
        with sqlite3.connect(app.config.database) as live:
            live.backup(self.rows)
        self.secrets = str(app.container.get(SecretValues).path)
        self.folders, files = self.tree()
        self.team_databases = {path: self.database_copy(path) for path in files if os.path.basename(path) == TEAM_DATABASE}
        kept = [path for path in files if not self.is_database(path)] + ([self.secrets] if os.path.isfile(self.secrets) else [])
        self.files = {path: Path(path).read_bytes() for path in kept}
        self.stamps = {path: self.stamp(path) for path in kept}
        self.instances = dict(app.container._instances)
        self.memory = ServiceMemory(self.instances.values())

    def reset(self) -> None:
        jobs = self.app.runtime().jobs
        running = jobs._thread is not None
        jobs.stop()
        self.app.container.get(ShellRunner).stop_runs()
        self.settled()
        self.put_back()
        if running:
            jobs.start()

    def put_back(self) -> None:
        self.app.container._instances.clear()
        self.app.container._instances.update(self.instances)
        self.memory.put_back()
        with sqlite3.connect(self.app.config.database) as live:
            self.rows.backup(live)
        for path, rows in self.team_databases.items():
            with sqlite3.connect(path) as live:
                rows.backup(live)
        self.app.container.get(Connection).cache.cleared()
        self.put_back_files()

    @staticmethod
    def database_copy(path: str) -> sqlite3.Connection:
        rows = sqlite3.connect(":memory:")
        with sqlite3.connect(path) as live:
            live.backup(rows)
        return rows

    def settled(self) -> None:
        if self.app.runtime().deferred._thread:
            self.app.runtime().deferred.drain()

    def tree(self) -> tuple[set[str], list[str]]:
        folders, files = set(), []
        for folder, inner, names in os.walk(self.app.config.root):
            folders.update(os.path.join(folder, name) for name in inner)
            files.extend(os.path.join(folder, name) for name in names)
        return folders, files

    def put_back_files(self) -> None:
        folders, files = self.tree()
        for path in files:
            if path not in self.files and not self.is_database(path):
                os.unlink(path)
        for path in sorted(folders - self.folders, reverse=True):
            if os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        if self.secrets not in self.files and os.path.isfile(self.secrets):
            os.unlink(self.secrets)
        for path, content in self.files.items():
            if self.stamp(path) != self.stamps[path]:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                Path(path).write_bytes(content)
                self.stamps[path] = self.stamp(path)

    @staticmethod
    def stamp(path: str) -> tuple:
        try:
            status = os.stat(path)
        except FileNotFoundError:
            return ()
        return status.st_mtime_ns, status.st_size

    def is_database(self, path: str) -> bool:
        name = os.path.basename(path)
        return name in (self.app.config.database.name, TEAM_DATABASE) or name.endswith(("-wal", "-shm", "-journal"))
