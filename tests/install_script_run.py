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


def test_the_journal_install_run_from_a_linked_worktree_installs_into_the_project_root(tmp_path: Path):
    script = (Path(__file__).resolve().parents[1] / "install.sh").read_text()
    start = script.index("# Run from a linked worktree")
    block = script[start:script.index("fi\n", start) + 3]
    project, worktree = tmp_path / "project", tmp_path / "project-worktree"
    project.mkdir()
    git = lambda *args, at=project: subprocess.run(["git", *args], cwd=at, capture_output=True, text=True, timeout=30, check=True)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "first")
    git("worktree", "add", "-q", str(worktree))
    (project / ".journal").mkdir()
    (worktree / ".journal").symlink_to(project / ".journal")
    ran = subprocess.run(["sh", "-c", f"{block}pwd -P"], cwd=worktree, capture_output=True, text=True, timeout=30)
    assert ran.stdout.strip() == str(project.resolve()), "the hooks and the journal command are written for the project, never the worktree"
    (worktree / ".journal").unlink()
    (worktree / ".journal").mkdir()
    ran = subprocess.run(["sh", "-c", f"{block}pwd -P"], cwd=worktree, capture_output=True, text=True, timeout=30)
    assert ran.stdout.strip() == str(worktree.resolve()), "a worktree with a journal of its own installs where it is"
