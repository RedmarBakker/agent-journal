import json
import os
import socket
import tempfile
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit

from journal.http.support.json_out import JsonOut
from journal.launcher.launch import Launch
from journal.launcher.menu import Menu
from journal.launcher.support.page_wait import PageWait
from journal.providers.support.status_line import StatusLine
from journal.support.worktree import Worktree
from tests.in_process import routed


class LauncherSteps:
    """What the launcher tells the viewer when its page is already open."""

    def launcher_starts_viewer_in(self, environment: str):
        def answered(request, timeout=0.5):
            address = request if isinstance(request, str) else request.full_url
            method = "GET" if isinstance(request, str) else request.get_method()
            headers = {} if isinstance(request, str) else dict(request.header_items())
            response = routed(self.app, method, urlsplit(address).path + (f"?{urlsplit(address).query}" if urlsplit(address).query else ""), request.data if not isinstance(request, str) else b"", headers)
            body = JsonOut.encoded(response.body)
            return nullcontext(SimpleNamespace(status=response.status, read=lambda: body))

        self.monkeypatch.setattr("urllib.request.urlopen", answered)
        lines = []
        page = PageWait(self.app.config.root / ".journal" / "port", "", ("journal", environment), f"?env={environment}", lines.append)
        page.shown("http://journal/")
        self.viewer_status, self.viewer_answer = 200, {"log": "\n".join(lines)}
        return self.observed(f"the launcher starts the viewer in {environment}", None, None)

    def launcher_starts_new_environment_with_live_main(self, environment: str):
        inbox = self.app.config.home / "runtime" / "inboxes" / "main"
        socket_path = Path(tempfile.gettempdir()) / f"journal-live-{os.getpid()}.sock"
        previous = inbox.read_text() if inbox.is_file() else None
        questions = []
        live = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        inbox.parent.mkdir(parents=True, exist_ok=True)
        socket_path.unlink(missing_ok=True)
        try:
            live.bind(str(socket_path))
            inbox.write_text(json.dumps({"socket": str(socket_path), "protocol": 0}))

            def picked(heading, notes, options, default):
                questions.append((heading, tuple(option.label for option in options), default))
                return default

            screen = SimpleNamespace(
                banner=lambda *args: None,
                choice=lambda heading, notes, options, default, actions: (len(options) - 1, ""),
                ask=lambda prompt: environment,
                pick=picked,
                summary=lambda rows: None,
            )
            launch = Launch.parse([self.provider], self.app.config.root)
            choice = Menu(self.app.config.root, launch.package / "journal.sh", screen).choose(self.provider)
            launch = launch.chosen(choice)
            launch.prepare_worktree(choice)
            worktree = Worktree(self.app.config.root, environment)
            if worktree.path.is_dir():
                self.closers.append(lambda: worktree.removed())
            refusal = launch.start_refusal(choice)
            launch_file = launch.launch_file(choice, StatusLine(self.app.config.root)) if not refusal else {}
        finally:
            live.close()
            socket_path.unlink(missing_ok=True)
            if previous is None:
                inbox.unlink(missing_ok=True)
            else:
                inbox.write_text(previous)
        self.launcher_questions = questions
        self.launcher_choice = choice
        self.launcher_refusal = refusal
        self.launcher_front_folder = launch_file.get("front", {}).get("folder", "")
        return self.observed(f"the launcher starts {environment} while main holds its branch", None, None)
