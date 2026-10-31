import array
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

from journal.config import Config
from journal.support.workspace_worktree import WorkspaceWorktree

# the launch switches of an agent nobody sits at: no questions, no browser, no journal of its own
DETACHED = ("--yes", "--no-open", "--no-journal")


class AgentLauncher:
    """Starts an agent for an environment from the running journal: its supervisor runs detached, with no journal of its own and no terminal, and its screen goes to a log under the runtime folder; in a worktree of its environment's name it skips the provider's prompts, as workers do, and carries on the conversation it is given to resume."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def start(self, environment: str, agent: str) -> int:
        return self.launched(environment, [agent, "--env", environment, *DETACHED])

    def start_in_worktree(self, environment: str, agent: str, resume: tuple[str, ...], repositories: tuple[str, ...] | None = None) -> int:
        worktree = WorkspaceWorktree.chosen(self.config.root, environment, repositories).created()
        return self.launched(environment, [agent, "--env", environment, "--worktree", environment, *DETACHED, "--skip", "--", *resume], worktree)

    def launched(self, environment: str, arguments: list[str], worktree: Path | None = None) -> int:
        package = Path(__file__).resolve().parents[2]
        log = self.config.home / "runtime" / f"agent-{environment}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        port = self.config.port_file.read_text().strip() if self.config.port_file.is_file() else str(self.config.port)
        if environment.startswith("plan-") and os.environ.get("JOURNAL_PLAN_DRIVER_SOCKET"):
            self.plan_worktree_permissions(worktree)
            return self.plan_launched(environment, arguments, worktree, log, port)
        environ = self.launch_environment(environment, port)
        with log.open("ab") as output:
            started = subprocess.Popen([sys.executable, str(package / "journal.py"), *arguments], cwd=self.config.root, env=environ, stdin=subprocess.DEVNULL, stdout=output, stderr=output, start_new_session=True)
        return started.pid

    def plan_launched(self, environment: str, arguments: list[str], worktree: Path | None, log: Path, port: str) -> int:
        if worktree is None:
            raise RuntimeError("the restricted Plan driver requires its plan worktree")
        prefix = ["codex", "--env", environment, "--worktree", environment, *DETACHED, "--skip", "--"]
        if arguments[:len(prefix)] != prefix:
            raise ValueError("the restricted Plan driver only accepts the fixed Codex plan command")
        request = json.dumps({
            "environment": environment,
            "root": str(self.config.root.resolve()),
            "worktree": str(worktree.resolve()),
            "port": port,
            "resume": arguments[len(prefix):],
        }).encode()
        with log.open("ab") as output, socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.connect(os.environ["JOURNAL_PLAN_DRIVER_SOCKET"])
            sent = connection.sendmsg([request], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [output.fileno()]))])
            if sent < len(request):
                connection.sendall(request[sent:])
            connection.shutdown(socket.SHUT_WR)
            response = json.loads(connection.recv(4096))
        if "error" in response:
            raise RuntimeError(f"the restricted Plan driver refused to start: {response['error']}")
        return int(response["pid"])

    def plan_worktree_permissions(self, worktree: Path | None) -> None:
        if worktree is None:
            raise RuntimeError("the restricted Plan driver requires its plan worktree")
        if worktree.is_symlink() or worktree.resolve() != worktree:
            raise PermissionError("the Plan driver worktree cannot resolve through a symbolic link")
        for folder in (self.config.root.parent, self.config.root, self.config.root / ".claude", worktree.parent):
            details = folder.stat()
            driver_can_traverse = (details.st_uid == 10003 and details.st_mode & 0o100) or (details.st_gid == 10003 and details.st_mode & 0o010) or (details.st_uid != 10003 and details.st_gid != 10003 and details.st_mode & 0o001)
            if driver_can_traverse:
                continue
            if details.st_uid != os.geteuid():
                raise PermissionError(f"the Plan driver cannot traverse {folder}")
            subprocess.run(["setfacl", "-m", "u:10003:--x", "--", str(folder)], check=True)
        subprocess.run(["find", str(worktree), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "setfacl", "-m", "u:10003:rwX", "--", "{}", "+"], check=True)
        subprocess.run(["setfacl", "-m", "d:u:10003:rwx", "--", str(worktree)], check=True)

    def launch_environment(self, environment: str, port: str) -> dict[str, str]:
        environ = {**os.environ, "JOURNAL_ROOT": str(self.config.root), "JOURNAL_PORT": port}
        codex_home = os.environ.get("JOURNAL_CODEX_HOME")
        if codex_home:
            if environment.startswith("plan-"):
                environ["CODEX_HOME"] = codex_home
            else:
                environ.pop("CODEX_HOME", None)
        return environ
