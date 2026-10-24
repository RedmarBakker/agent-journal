# Starts a fake ssh as a process, so it is not in the default run: python3 -m pytest -q tests/remote_install_run.py
"""journal remote install runs the release's team installer on a machine over ssh -t, so its questions reach the terminal, and refuses an agent's shell, which has no terminal."""
import os
import subprocess
import sys
from pathlib import Path

from journal.launcher.remote_install import RemoteInstall
from journal.version import VERSION

PACKAGE = Path(__file__).resolve().parents[1] / "src"


def test_the_installer_runs_over_ssh_with_a_terminal_and_this_journals_release(tmp_path: Path, monkeypatch):
    seen = tmp_path / "ssh-args"
    fake = tmp_path / "bin" / "ssh"
    fake.parent.mkdir()
    fake.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{seen}"\necho "journal team join https://203.0.113.5 --code ABC"\n')
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake.parent}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    assert RemoteInstall.parsed(["install", "root@203.0.113.5"]).run() == 0
    args = seen.read_text().splitlines()
    assert args[:2] == ["-t", "root@203.0.113.5"], "ssh is given a terminal and the machine"
    assert args[2] == f"curl -fsSL https://github.com/jessegall/agent-journal/releases/download/v{VERSION}/install.sh | TEAM_ADDRESS=203.0.113.5 sh", "and runs this journal's own release of the installer"


def test_an_agents_shell_with_no_terminal_is_told_to_run_it_in_a_terminal(tmp_path: Path):
    ran = subprocess.run([sys.executable, str(PACKAGE / "journal.py"), "remote", "install", "root@203.0.113.5"], capture_output=True, text=True, stdin=subprocess.DEVNULL, cwd=tmp_path, timeout=20)
    assert ran.returncode == 2 and "run it in yours" in ran.stderr
