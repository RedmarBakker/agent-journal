import fcntl
import shutil
import subprocess
from pathlib import Path

from journal.support.inner_repositories import InnerRepositories
from journal.support.rejection import Rejection
from journal.support.worktree import JOURNAL, SKILL_FOLDERS, Worktree
from journal.support.worktree_failure import WorktreeFailure

# what a launch folder links from the project beside its repositories' worktrees, when the project holds them
SHARED_ENTRIES = (JOURNAL, ".claude/settings.json", ".claude/settings.local.json", ".codex", "CLAUDE.md", "AGENTS.md")


class WorkspaceWorktree(Worktree):
    """A launch's worktree in a project folder that is no git repository but holds several: a folder at .claude/worktrees/<name> holding a worktree of each inner repository on the branch worktree-<name>, with the project's journal, settings and skills linked beside them."""

    @classmethod
    def chosen(cls, root: Path, name: str) -> Worktree:
        is_repository = InnerRepositories.git(root, "rev-parse", "--git-dir").returncode == 0
        return cls(root, name) if not is_repository and InnerRepositories(root).names() else Worktree(root, name)

    def repositories(self) -> tuple[str, ...]:
        return InnerRepositories(self.root).names()

    def created(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with (self.path.parent / f".{self.name}.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if not self.path.is_dir():
                self.added()
            for entry in (*SHARED_ENTRIES, *(f"{folder}/{skill.name}" for folder in SKILL_FOLDERS if (self.root / folder).is_dir() for skill in sorted((self.root / folder).iterdir()))):
                if (self.root / entry).exists():
                    self.linked(self.path / entry, self.root / entry)
        return self.path

    def added(self) -> None:
        self.path.mkdir()
        worktree_repositories: list[str] = []
        for repository in self.repositories():
            source = self.root / repository
            exists = self.answered(["git", "-C", str(source), "rev-parse", "--verify", "--quiet", f"refs/heads/{self.branch}"]).returncode == 0
            added = self.answered(["git", "-C", str(source), "worktree", "add", "-q", *([str(self.path / repository), self.branch] if exists else ["-b", self.branch, str(self.path / repository)])])
            if added.returncode != 0:
                for added_repository in worktree_repositories:
                    self.answered(["git", "-C", str(self.root / added_repository), "worktree", "remove", "--force", str(self.path / added_repository)])
                shutil.rmtree(self.path, ignore_errors=True)
                raise WorktreeFailure(self.name, f"the repository {repository} gave no worktree: {self.add_refusal(added.stderr.strip())}")
            worktree_repositories.append(repository)

    def uncommitted(self) -> list[str]:
        return [f"{repository}/{line[3:]}" for repository in self.repositories() if (self.path / repository).is_dir() for line in self.inner_git(repository, "status", "--porcelain").stdout.splitlines() if line.strip()]

    def removed(self) -> None:
        for repository in self.repositories():
            if not (self.path / repository).exists():
                continue
            removal = self.answered(["git", "-C", str(self.root / repository), "worktree", "remove", str(self.path / repository)])
            if removal.returncode != 0:
                raise Rejection(f"the worktree {self.name} could not be removed: the repository {repository} said {removal.stderr.strip()}")
        shutil.rmtree(self.path)

    def record_tip(self) -> None:
        return

    def is_registered(self) -> bool:
        return self.path.is_dir()

    def current_branch(self) -> str:
        return self.branch

    def inner_git(self, repository: str, *argv: str) -> subprocess.CompletedProcess:
        return self.answered(["git", "-C", str(self.path / repository), *argv])
