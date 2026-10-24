# Runs host/install.sh with a fake docker and curl as processes, so it is not in the default run: python3 -m pytest -q tests/install_script_run.py
"""host/install.sh, given the project and the address, asks nothing, starts the team server with a setup code and prints that code."""
import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "host" / "install.sh"


def fake(bin: Path, name: str, body: str) -> None:
    path = bin / name
    path.write_text(f"#!/bin/sh\n{body}\n")
    path.chmod(0o755)


def test_the_installer_runs_without_questions_from_its_settings_and_prints_the_setup_code(tmp_path: Path):
    bin, seen = tmp_path / "bin", tmp_path / "docker-args"
    bin.mkdir()
    fake(bin, "docker", f'case "$1" in volume) [ "$2" = inspect ] && exit 1; exit 0 ;; run) printf "%s\\n" "$@" > "{seen}" ;; esac; exit 0')
    fake(bin, "curl", 'printf 200')
    env = {**os.environ, "PATH": f"{bin}{os.pathsep}{os.environ['PATH']}", "TEAM_PROJECT": "Shop", "TEAM_ADDRESS": "203.0.113.5", "TEAM_SETUP_CODE": "ABCD-EFGH"}
    ran = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=30)
    assert ran.returncode == 0, ran.stderr
    assert "Its setup code is ABCD-EFGH" in ran.stdout and "--setup-code ABCD-EFGH" in ran.stdout
    args = seen.read_text().splitlines()
    assert "TEAM_SETUP_CODE=ABCD-EFGH" in args and "TEAM_ADDRESS=203.0.113.5" in args and "agent-journal-shop" in args, args


def test_the_installer_makes_its_own_setup_code_when_none_is_given(tmp_path: Path):
    bin = tmp_path / "bin"
    bin.mkdir()
    fake(bin, "docker", 'case "$1" in volume) [ "$2" = inspect ] && exit 1 ;; esac; exit 0')
    fake(bin, "curl", 'printf 200')
    env = {**os.environ, "PATH": f"{bin}{os.pathsep}{os.environ['PATH']}", "TEAM_PROJECT": "Shop", "TEAM_ADDRESS": "203.0.113.5"}
    env.pop("TEAM_SETUP_CODE", None)
    ran = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=30)
    code = ran.stdout.split("Its setup code is ")[1][:9]
    assert ran.returncode == 0 and code[4] == "-" and len(code.replace("-", "")) == 8, ran.stdout
