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
    """A launch's worktree in a project holding inner repositories: its project branch and selected inner branches share a name, with the project's journal, settings and skills linked beside them."""

    def __init__(self, root: Path, name: str, repositories: tuple[str, ...]) -> None:
        super().__init__(root, name)
        self.inner_repositories = repositories
        self.project_repository = InnerRepositories.git(root, "rev-parse", "--git-dir").returncode == 0

    @classmethod
    def chosen(cls, root: Path, name: str, repositories: tuple[str, ...] | None = None) -> Worktree:
        is_repository = InnerRepositories.git(root, "rev-parse", "--git-dir").returncode == 0
        available = InnerRepositories(root).names()
        if repositories is None:
            path = root / ".claude" / "worktrees" / name
            selected = available if not is_repository else tuple(repo for repo in available if (path / repo / ".git").exists())
        else:
            selected = tuple(repo for repo in repositories if repo in available)
        return cls(root, name, selected) if selected else Worktree(root, name)

    def repositories(self) -> tuple[str, ...]:
        if not self.path.is_dir():
            return self.inner_repositories
        return tuple(name for name in self.inner_repositories if (self.path / name / ".git").exists())

    def created(self) -> Path:
        if self.project_repository:
            return super().created()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with (self.path.parent / f".{self.name}.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if not self.path.is_dir():
                self.added()
            else:
                self.reused()
            for entry in (*SHARED_ENTRIES, *(f"{folder}/{skill.name}" for folder in SKILL_FOLDERS if (self.root / folder).is_dir() for skill in sorted((self.root / folder).iterdir()))):
                if (self.root / entry).exists():
                    self.linked(self.path / entry, self.root / entry)
        return self.path

    def added(self) -> None:
        if self.project_repository:
            super().added()
            if failure := self.add_inner_repositories():
                self.registration_dropped()
                raise failure
            return
        self.path.mkdir()
        worktree_repositories: list[str] = []
        for repository in self.inner_repositories:
            source = self.root / repository
            exists = self.answered(["git", "-C", str(source), "rev-parse", "--verify", "--quiet", f"refs/heads/{self.branch}"]).returncode == 0
            added = self.answered(["git", "-C", str(source), "worktree", "add", "-q", *([str(self.path / repository), self.branch] if exists else ["-b", self.branch, str(self.path / repository)])])
            if added.returncode != 0:
                for added_repository in worktree_repositories:
                    self.answered(["git", "-C", str(self.root / added_repository), "worktree", "remove", "--force", str(self.path / added_repository)])
                shutil.rmtree(self.path, ignore_errors=True)
                raise WorktreeFailure(self.name, f"the repository {repository} gave no worktree: {self.add_refusal(added.stderr.strip())}")
            worktree_repositories.append(repository)

    def reused(self) -> None:
        if failure := self.add_inner_repositories():
            raise failure

    def add_inner_repositories(self) -> WorktreeFailure | None:
        added_repositories = []
        for repository in self.inner_repositories:
            source = self.root / repository
            path = self.path / repository
            if (path / ".git").exists():
                continue
            exists = self.answered(["git", "-C", str(source), "rev-parse", "--verify", "--quiet", f"refs/heads/{self.branch}"]).returncode == 0
            added = self.answered(["git", "-C", str(source), "worktree", "add", "-q", *([str(path), self.branch] if exists else ["-b", self.branch, str(path), "HEAD"])])
            if added.returncode != 0:
                for prior in added_repositories:
                    self.answered(["git", "-C", str(self.root / prior), "worktree", "remove", "--force", str(self.path / prior)])
                return WorktreeFailure(self.name, f"the repository {repository} gave no worktree: {self.add_refusal(added.stderr.strip())}")
            added_repositories.append(repository)
        return None

    def uncommitted(self) -> list[str]:
        project = super().uncommitted() if self.project_repository else []
        inner = [f"{repository}/{line[3:]}" for repository in self.repositories() for line in self.inner_git(repository, "status", "--porcelain", "--untracked-files=all").stdout.splitlines() if line.strip()]
        return [*project, *inner]

    def removed(self) -> None:
        self.remove_inner_repositories()
        if self.project_repository:
            super().removed()
        else:
            shutil.rmtree(self.path)

    def removed_after_merge(self, allowed: list[str]) -> None:
        leftover = set(self.uncommitted()) - set(allowed)
        if leftover:
            raise Rejection(f"the worktree {self.name} has uncommitted files: {', '.join(sorted(leftover)[:10])}")
        self.remove_inner_repositories_after_merge()
        if self.project_repository:
            super().removed_after_merge(allowed)
            return
        shutil.rmtree(self.path)

    def remove_inner_repositories(self) -> None:
        self.remove_inner_repositories_with(())

    def remove_inner_repositories_after_merge(self) -> None:
        self.remove_inner_repositories_with(("--force",))

    def remove_inner_repositories_with(self, arguments: tuple[str, ...]) -> None:
        for repository in self.repositories():
            if not (self.path / repository).exists():
                continue
            removal = self.answered(["git", "-C", str(self.root / repository), "worktree", "remove", *arguments, str(self.path / repository)])
            if removal.returncode != 0:
                raise Rejection(f"the worktree {self.name} could not be removed: the repository {repository} answered {removal.stderr.strip()}")

    def record_tip(self) -> None:
        if not self.project_repository:
            return
        super().record_tip()

    def is_registered(self) -> bool:
        return super().is_registered() if self.project_repository else self.path.is_dir()

    def current_branch(self) -> str:
        return super().current_branch() if self.project_repository else self.branch

    def shared(self) -> None:
        if self.project_repository:
            super().shared()
        for entry in (*SHARED_ENTRIES, *(f"{folder}/{skill.name}" for folder in SKILL_FOLDERS if (self.root / folder).is_dir() for skill in sorted((self.root / folder).iterdir()))):
            if (self.root / entry).exists():
                self.linked(self.path / entry, self.root / entry)

    def inner_git(self, repository: str, *argv: str) -> subprocess.CompletedProcess:
        return self.answered(["git", "-C", str(self.path / repository), *argv])
