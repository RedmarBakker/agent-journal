# Runs the launcher's journal commands as processes against a real server, so it is not in the default run: python3 -m pytest -q tests/launch_commands_run.py
"""A launch's journal commands go through the running server, so what they write is in the lists the viewer reads at once."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pytest

from journal.app import App
from journal.config import Config
from journal.launcher.menu import Menu
from tests.main_journal import main_journal

SHELL_ENTRY = Path(__file__).resolve().parent.parent / "src" / "journal.sh"


@pytest.fixture(scope="module")
def boot():
    def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
        app = main_journal(Config(root, port=0))
        app.runtime().boot()
        app.server().start()
        return app
    return booted


def environment_names(port: int) -> set[str]:
    with urlopen(Request(f"http://127.0.0.1:{port}/journal/environments", headers={"X-Journal-Env": "main"}), timeout=5) as reply:
        return {row["name"] for row in json.loads(reply.read())["rows"]}


def test_an_environment_a_launch_creates_is_in_the_list_the_sidebar_reads_at_once(app: App):
    server = app.server()
    (app.config.home / "port").write_text(str(server.port))
    assert "1024-test" not in environment_names(server.port), "the list is read, and kept in memory, before the launch"
    Menu(app.config.root, SHELL_ENTRY).journal("environment", "create", "1024-test")
    assert "1024-test" in environment_names(server.port), "the environment the launch created is in the list at once, without a restart"
