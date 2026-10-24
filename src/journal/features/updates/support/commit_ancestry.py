import subprocess

from journal.config import Config

GIT_SECONDS = 60
ASKED_WRONG = 128


class CommitAncestry:
    """Whether a branch's head is ahead of the installed commit, by asking git in the project checkout whether the installed commit is the head's ancestor, fetching the branch once when the checkout does not hold the head yet."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def is_ahead(self, head: str, installed: str, repository: str, branch: str) -> bool:
        if not installed:
            return True
        code = self.ancestor_code(installed, head)
        if code == ASKED_WRONG:
            subprocess.run(["git", "fetch", "--quiet", repository, branch], cwd=self.config.root, capture_output=True, timeout=GIT_SECONDS)
            code = self.ancestor_code(installed, head)
        return code == 0

    def ancestor_code(self, installed: str, head: str) -> int:
        return subprocess.run(["git", "merge-base", "--is-ancestor", installed, head], cwd=self.config.root, capture_output=True, timeout=GIT_SECONDS).returncode
