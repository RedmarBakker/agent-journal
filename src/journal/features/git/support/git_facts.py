import shlex
import subprocess
from pathlib import Path

from journal.events.event import Event
from journal.events.moments.branch_changed import BranchChanged
from journal.events.moments.git_committed import GitCommitted
from journal.events.moments.git_pushed import GitPushed

GIT_SECONDS = 10
SWITCHING = ("checkout", "switch")


class GitFacts:
    """What a git command that ended well left in its folder, as the event it is worth: the commit at the head for a commit, the branch and the remote for a push, the branch now on for a checkout or a switch that names one."""

    @staticmethod
    def event(part: str, folder: Path, environment_id: int, session: str | None) -> Event | None:
        try:
            tokens = shlex.split(part)
        except ValueError:
            return None
        if tokens[:1] != ["git"] or len(tokens) < 2:
            return None
        verb, arguments = tokens[1], [word for word in tokens[2:] if not word.startswith("-")]
        if verb == "commit" and "--dry-run" not in tokens:
            return GitFacts.commit(folder, environment_id, session)
        if verb == "push" and "--delete" not in tokens:
            return GitPushed(environment_id=environment_id, session=session, branch=GitFacts.pushed_branch(arguments, folder), remote=arguments[0] if arguments else "origin")
        if verb in SWITCHING and arguments and "--" not in tokens and GitFacts.branch(folder) == arguments[-1]:
            return BranchChanged(environment_id=environment_id, session=session, branch=arguments[-1])
        return None

    @staticmethod
    def run(folder: Path, *arguments: str) -> str:
        process = subprocess.run(["git", "-C", str(folder), *arguments], capture_output=True, text=True, timeout=GIT_SECONDS)
        return process.stdout.strip() if process.returncode == 0 else ""

    @staticmethod
    def branch(folder: Path) -> str:
        return GitFacts.run(folder, "rev-parse", "--abbrev-ref", "HEAD")

    @staticmethod
    def pushed_branch(arguments: list[str], folder: Path) -> str:
        return arguments[1].split(":")[-1] if len(arguments) > 1 else GitFacts.branch(folder)

    @staticmethod
    def commit(folder: Path, environment_id: int, session: str | None) -> GitCommitted | None:
        head = GitFacts.run(folder, "log", "-1", "--format=%H%x00%s")
        if not head:
            return None
        sha, _, subject = head.partition("\0")
        changed = GitFacts.run(folder, "show", "--numstat", "--format=", "HEAD").splitlines()
        return GitCommitted(environment_id=environment_id, session=session, sha=sha, branch=GitFacts.branch(folder), subject=subject, files=len(changed))
