# Runs install.sh as a real process over a version 3 journal, so it is not in the default run: python3 -m pytest tests/install_process.py
import subprocess
from pathlib import Path

INSTALL = Path(__file__).resolve().parent.parent / "install.sh"


def installed_over_version_3(tmp_path: Path, setup_code: int, confirmed: str = "1", version: str = "3.3.5") -> subprocess.CompletedProcess:
    """A journal from before version 4, and a stand-in python that passes the version check and ends setup with the given code, so no journal starts."""
    (tmp_path / ".journal" / "src").mkdir(parents=True)
    (tmp_path / ".journal" / "src" / "VERSION").write_text(f"{version}\n")
    (tmp_path / ".journal" / "project").mkdir()
    (tmp_path / ".journal" / "project" / "message-1.json").write_text("{}")
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    (bin_ / "python3").write_text(f'#!/bin/sh\n[ "$1" = -c ] && exit 0\nexit {setup_code}\n')
    (bin_ / "python3").chmod(0o755)
    return subprocess.run(["sh", str(INSTALL)], cwd=tmp_path, env={"PATH": f"{bin_}:/usr/bin:/bin", "HOME": str(tmp_path), "AGENT_JOURNAL_YES": confirmed}, capture_output=True, text=True, timeout=120)


def test_installing_over_a_version_3_journal_keeps_it_whole_in_version_3(tmp_path: Path):
    run = installed_over_version_3(tmp_path, 0)
    assert run.returncode == 0, run.stderr
    assert (tmp_path / ".journal" / "version-3" / "project" / "message-1.json").is_file(), "the version 3 journal is kept whole"
    assert (tmp_path / ".journal" / "src" / "journal").is_dir() and not (tmp_path / ".journal" / "src" / "VERSION").exists(), "version 4 is installed beside it"


def test_a_failed_install_puts_the_version_3_journal_back(tmp_path: Path):
    run = installed_over_version_3(tmp_path, 1)
    assert run.returncode != 0 and "back where it was" in run.stderr, run.stderr
    assert (tmp_path / ".journal" / "src" / "VERSION").read_text() == "3.3.5\n" and (tmp_path / ".journal" / "project" / "message-1.json").is_file()
    assert not (tmp_path / ".journal" / "version-3").exists() and not (tmp_path / ".journal-version-3").exists()


def test_without_a_yes_the_installer_changes_nothing(tmp_path: Path):
    run = installed_over_version_3(tmp_path, 0, confirmed="")
    assert run.returncode == 0 and "Nothing changed" in run.stdout, run.stdout
    assert (tmp_path / ".journal" / "src" / "VERSION").read_text() == "3.3.5\n" and not (tmp_path / ".journal" / "version-3").exists()


def test_a_journal_numbered_2_is_from_before_version_4_too_and_kept_whole(tmp_path: Path):
    run = installed_over_version_3(tmp_path, 0, version="2.272.14")
    assert run.returncode == 0, run.stderr
    assert (tmp_path / ".journal" / "version-3" / "project" / "message-1.json").is_file() and (tmp_path / ".journal" / "version-3" / "src" / "VERSION").read_text() == "2.272.14\n", "a 2.x journal is backed up whole like a 3.x one"


def stub_checkout(project: Path) -> None:
    """A git project holding install.sh and the parts it copies, with a stand-in python that passes the version check and ends setup."""
    for name in ("journal", "supervisor", "sync_server", "web/dist"):
        (project / "src" / name).mkdir(parents=True, exist_ok=True)
        (project / "src" / name / "file.txt").write_text(name)
    for name in ("journal.py", "journal.sh"):
        (project / "src" / name).write_text("")
    (project / "install.sh").write_text(INSTALL.read_text())
    bin_ = project / "bin"
    bin_.mkdir()
    (bin_ / "python3").write_text("#!/bin/sh\nexit 0\n")
    (bin_ / "python3").chmod(0o755)
    (project / ".gitignore").write_text("bin/\n.journal\n")


def git(at: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a", *args], cwd=at, capture_output=True, text=True, timeout=30, check=True).stdout.strip()


def test_the_install_alias_run_from_a_worktree_installs_the_project_checkouts_head_and_prints_it(tmp_path: Path):
    """The alias is `sh install.sh`, run in the folder of the environment: a worktree cut from an old commit installs the project's head, not its own."""
    project, worktree = tmp_path / "project", tmp_path / "worktree"
    project.mkdir()
    git(project, "init", "-q")
    stub_checkout(project)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "old")
    git(project, "worktree", "add", "-q", "--detach", str(worktree))
    (project / "src" / "journal" / "newer.txt").write_text("a day of fixes")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "new")
    head = git(project, "rev-parse", "HEAD")
    assert git(worktree, "rev-parse", "HEAD") != head
    (project / ".journal").mkdir()
    (worktree / ".journal").symlink_to(project / ".journal")
    run = subprocess.run(["sh", "-c", "sh install.sh"], cwd=worktree, env={"PATH": f"{project / 'bin'}:/usr/bin:/bin", "HOME": str(tmp_path), "AGENT_JOURNAL_YES": "1"}, capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr
    assert (project / ".journal" / "src" / "commit").read_text().strip() == head
    assert (project / ".journal" / "src" / "journal" / "newer.txt").is_file(), "the code installed is the project's"
    assert f"installed commit {head}" in run.stdout, run.stdout


def test_an_install_that_cannot_name_its_commit_fails_loudly(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    stub_checkout(project)
    run = subprocess.run(["sh", "install.sh"], cwd=project, env={"PATH": f"{project / 'bin'}:/usr/bin:/bin", "HOME": str(tmp_path), "AGENT_JOURNAL_YES": "1", "GIT_CEILING_DIRECTORIES": str(tmp_path)}, capture_output=True, text=True, timeout=120)
    assert run.returncode != 0 and "the commit installed cannot be known" in run.stderr, run.stderr
