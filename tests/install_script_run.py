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


def test_a_daemon_that_never_starts_is_reported_with_its_own_last_lines(tmp_path: Path):
    bin = tmp_path / "bin"
    bin.mkdir()
    fake(bin, "docker", 'case "$1" in info) exit 1 ;; esac; exit 0')
    fake(bin, "systemctl", "exit 1")
    fake(bin, "service", "exit 1")
    fake(bin, "sudo", '"$@"')
    fake(bin, "sleep", "exit 0")
    fake(bin, "journalctl", 'echo "dockerd: iptables (nf_tables): Could not fetch rule set generation id: Invalid argument"')
    env = {**os.environ, "PATH": f"{bin}{os.pathsep}{os.environ['PATH']}", "TEAM_PROJECT": "Shop", "TEAM_ADDRESS": "203.0.113.5"}
    ran = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=30)
    assert ran.returncode == 1 and "its daemon does not start. Its last lines:" in ran.stderr and "Could not fetch rule set generation id" in ran.stderr, ran.stderr


def test_a_rescue_system_is_named_as_one_before_any_wait(tmp_path: Path):
    bin = tmp_path / "bin"
    bin.mkdir()
    fake(bin, "docker", "exit 0")
    fake(bin, "hostname", "echo rescue")
    env = {**os.environ, "PATH": f"{bin}{os.pathsep}{os.environ['PATH']}", "TEAM_PROJECT": "Shop", "TEAM_ADDRESS": "203.0.113.5"}
    ran = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=30)
    assert ran.returncode == 1 and "This machine runs a rescue system, which cannot run Docker: install an operating system" in ran.stderr, ran.stderr


def test_a_piped_installer_asks_on_the_terminal_and_runs_to_its_end(tmp_path: Path):
    """Run as curl | sh, the script arrives on standard input while the prompts read the terminal; it is read whole before it runs, so an answer never cuts it short, and each step says what it does."""
    import pty
    import select
    bin = tmp_path / "bin"
    bin.mkdir()
    fake(bin, "docker", 'case "$1" in volume) [ "$2" = inspect ] && exit 1; exit 0 ;; esac; exit 0')
    fake(bin, "curl", 'printf 200')
    env = {**os.environ, "PATH": f"{bin}{os.pathsep}{os.environ['PATH']}", "TEAM_ADDRESS": "203.0.113.5", "TEAM_SETUP_CODE": "ABCD-EFGH"}
    leader, follower = pty.openpty()
    piped = subprocess.Popen(["sh", "-c", f"cat '{SCRIPT}' | sh"], stdin=follower, stdout=follower, stderr=follower, env=env, start_new_session=True, preexec_fn=lambda: os.login_tty(follower))
    os.close(follower)
    printed = b""
    while b"Project name" not in printed and select.select([leader], [], [], 10)[0]:
        printed += os.read(leader, 4096)
    os.write(leader, b"Shop\n")
    while select.select([leader], [], [], 10)[0]:
        try:
            chunk = os.read(leader, 4096)
        except OSError:
            break
        if not chunk:
            break
        printed += chunk
    piped.wait(timeout=30)
    text = printed.decode(errors="replace")
    assert piped.returncode == 0, text
    assert "Pulling the team server's image" in text and "Starting the team server in the container agent-journal-shop" in text and "Waiting for https://203.0.113.5 to answer" in text, text
    assert "Its setup code is ABCD-EFGH" in text, "the script ran to its end after the answer"


def test_a_team_server_that_asks_for_a_newer_protocol_counts_as_answering(tmp_path: Path):
    """The check at the end asks in protocol 1; a newer team server answers 426, upgrade first, which still means it runs behind its certificate."""
    bin = tmp_path / "bin"
    bin.mkdir()
    fake(bin, "docker", 'case "$1" in volume) [ "$2" = inspect ] && exit 1; exit 0 ;; esac; exit 0')
    fake(bin, "curl", 'printf 426')
    env = {**os.environ, "PATH": f"{bin}{os.pathsep}{os.environ['PATH']}", "TEAM_PROJECT": "Shop", "TEAM_ADDRESS": "203.0.113.5", "TEAM_SETUP_CODE": "ABCD-EFGH"}
    ran = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=30)
    assert ran.returncode == 0 and "Its setup code is ABCD-EFGH" in ran.stdout, ran.stderr
    assert "with the server's own certificate, which an IP address gets" in ran.stderr, ran.stderr
