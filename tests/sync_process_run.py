# This file starts the sync carrier as a process of its own against a journal server and a team server, so it is not in the default run: python3 -m pytest tests/sync_process_run.py
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from journal.app import App
from journal.config import Config
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.support.caller import Caller
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from sync_server.account import ADMIN
from sync_server.login_request import LoginRequest
from sync_server.team_server import TeamServer

from main_journal import main_journal

PACKAGE = Path(__file__).resolve().parents[1] / "src"
USER = Caller.user("main")


@pytest.fixture(scope="module")
def boot():
    return booted


def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
    patch.setattr(Config, "status_home", property(lambda self: root / "status"))
    app = main_journal(Config(root, port=0))
    app.runtime().start()
    return app


def eventually(check, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if check():
            return True
        time.sleep(0.1)
    return check()


def carrier(app: App) -> subprocess.Popen:
    environ = {**os.environ, "JOURNAL_ROOT": str(app.config.root), "PYTHONPATH": str(PACKAGE), "PYTHONFAULTHANDLER": "1", "JOURNAL_ENV": "main"}
    return subprocess.Popen([sys.executable, str(PACKAGE / "journal.py"), "sync"], env=environ, stdout=subprocess.DEVNULL, stderr=open(app.config.root / "carrier.log", "a"))


def test_the_carrier_in_a_process_of_its_own_sends_the_journals_changes_once_and_takes_the_teams_through_the_local_doors(app: App):
    folder = app.config.root / "team-server"
    folder.mkdir()
    team = TeamServer(folder)
    team.accounts.create("ada@example.com", "Ada", "correct horse battery", ADMIN, 1.0)
    server = team.started("127.0.0.1", 0)
    answer = team.logins.answer(LoginRequest("ada@example.com", "correct horse battery", "ada-laptop"), "127.0.0.1")
    account = app.container.get(TeamAccount)
    account.write({"address": f"http://127.0.0.1:{server.server_address[1]}", "token": answer.token, "device": answer.device_id, "sequence": 0})
    app.server()
    app.container.get(OutgoingChanges).clear()
    process = carrier(app)
    try:
        made = app.console().run(["task", "create", "sent by the carrier"], USER)
        assert made.code == 0, made.error
        titles = lambda: [row.fields.get("title") for row in team.log.copied_rows() if row.row_table == "tasks"]
        sent = eventually(lambda: "sent by the carrier" in titles(), 20)
        if not sent:
            process.send_signal(signal.SIGABRT)
            process.wait(10)
        assert sent, f"alive {process.poll() is None}, waiting {len(app.container.get(OutgoingChanges).waiting())}, team {titles()}, log {(app.config.root / 'carrier.log').read_text()[:2500]}"
        process.send_signal(signal.SIGKILL)
        process.wait(10)
        status = app.container.get(SyncStatus)
        assert eventually(lambda: status.line() == "Not connected: the sync process is not running", 15), "a killed carrier shows as not connected within seconds"
        app.console().run(["task", "create", "made while the carrier was down"], USER)
        process = carrier(app)
        assert eventually(lambda: "made while the carrier was down" in titles(), 20), "a carrier started again sends what waited"
        assert titles().count("made while the carrier was down") == 1, "and sends it once"
        assert eventually(lambda: app.container.get(OutgoingChanges).waiting() == [], 10), "the queue empties as the team takes it"
    finally:
        process.send_signal(signal.SIGTERM)
        process.wait(10)
        account.left(0)
        server.shutdown()


def test_the_carrier_ends_when_the_process_that_started_it_is_killed(app: App):
    folder = app.config.root / "team-server"
    folder.mkdir(exist_ok=True)
    team = TeamServer(folder)
    team.accounts.create("ada@example.com", "Ada", "correct horse battery", ADMIN, 1.0)
    server = team.started("127.0.0.1", 0)
    answer = team.logins.answer(LoginRequest("ada@example.com", "correct horse battery", "ada-laptop"), "127.0.0.1")
    account = app.container.get(TeamAccount)
    account.write({"address": f"http://127.0.0.1:{server.server_address[1]}", "token": answer.token, "device": answer.device_id, "sequence": 0})
    pid_file = app.config.root / "carrier.pid"
    environ = {**os.environ, "JOURNAL_ROOT": str(app.config.root), "PYTHONPATH": str(PACKAGE), "JOURNAL_ENV": "main", "PYTHONFAULTHANDLER": "1"}
    log = app.config.root / "orphan.log"
    # a stand-in for the supervisor: a parent that starts the carrier and waits on it, killed as a supervisor killed with SIGKILL would be
    starter = f"import os, subprocess, sys; carrier = subprocess.Popen([sys.executable, {str(PACKAGE / 'journal.py')!r}, 'sync'], stderr=open({str(log)!r}, 'w'), env={{**os.environ, 'JOURNAL_PARENT_PID': str(os.getpid())}}); open({str(pid_file)!r}, 'w').write(str(carrier.pid)); carrier.wait()"
    parent = subprocess.Popen([sys.executable, "-c", starter], env=environ)
    try:
        assert eventually(lambda: pid_file.is_file() and pid_file.read_text().strip(), 10)
        carrier_pid = int(pid_file.read_text())
        alive = lambda: subprocess.run(["kill", "-0", str(carrier_pid)], capture_output=True).returncode == 0
        assert eventually(alive, 5)
        parent.send_signal(signal.SIGKILL)
        parent.wait(10)
        gone = eventually(lambda: not alive(), 10)
        if not gone:
            os.kill(carrier_pid, signal.SIGABRT)
            time.sleep(2)
        assert gone, log.read_text()[-4000:]
    finally:
        account.left(0)
        server.shutdown()
