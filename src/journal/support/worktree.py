import fcntl
import os
import shutil
import subprocess
from pathlib import Path

from journal.support.worktree_refs import TIPS_REF
from journal.support.rejection import Rejection
from journal.support.worktree_failure import WorktreeFailure

GIT_SECONDS = 60
JOURNAL = ".journal"
SKILL_FOLDERS = (".claude/skills", ".agents/skills")
# the link a worktree reads the journal's hooks through, never a file of the project's own
LOCAL_SETTINGS = ".claude/settings.local.json"
# the settings a worktree reads through a link to a file the main checkout's journal writes, kept out of git in every worktree
LINKED_SETTINGS = (LOCAL_SETTINGS, ".codex/hooks.json")
IGNORED_COPIES = (".claude/settings.json", ".codex/hooks.json", ".codex/agents", ".claude/agents", "AGENTS.md", "CLAUDE.md")


class Worktree:
    """The git worktree a launch works in, at .claude/worktrees/<name> on the branch worktree-<name>, where Claude Code keeps its own: made when it is not there, and never removed by the journal or handed to the agent to remove."""

    def __init__(self, root: Path, name: str, git_seconds: float = GIT_SECONDS) -> None:
        self.root, self.name, self.git_seconds = root, name, git_seconds

    @property
    def path(self) -> Path:
        return self.root / ".claude" / "worktrees" / self.name

    @property
    def folder(self) -> Path:
        return self.path if self.path.is_dir() else self.root

    @property
    def branch(self) -> str:
        return f"worktree-{self.name}"

    def badges(self) -> tuple[str, ...]:
        if not self.path.is_dir():
            return ()
        return (f"worktree on {self.current_branch()}",)

    def current_branch(self) -> str:
        return self.run_git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()

    def created(self) -> Path:
        self.project_check()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with (self.path.parent / f".{self.name}.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if self.path.exists() and not self.is_registered():
                raise WorktreeFailure(self.name, f"{self.path} is there but git does not hold it as a worktree, so it is left as it is: move it away, or add it back with git worktree add")
            if not self.path.is_dir():
                self.added()
            self.shared()
            self.record_tip()
        return self.path

    # the kept tip only moves forward: a lost folder, or a branch moved back, never takes the last real tip away
    def record_tip(self) -> None:
        tip = self.local_branch() if self.path.is_dir() else ""
        tip_ref = f"{TIPS_REF}/{self.name}"
        if not tip or (self.has(tip_ref) and self.git("merge-base", "--is-ancestor", tip_ref, tip).returncode != 0):
            return
        self.git("update-ref", tip_ref, tip)

    # the folder, the branch and the kept tip move to the new name together, whichever of them is still there
    def renamed(self, name: str) -> "Worktree":
        target = Worktree(self.root, name)
        if target.path.exists() or target.has(f"refs/heads/{target.branch}") or target.has(f"{TIPS_REF}/{name}"):
            raise Rejection(f"the name {name} still has a worktree, a branch {target.branch} or a kept tip left from earlier: journal worktree remove {name} or git branch -D {target.branch} frees it, or choose another name")
        steps = []
        if self.path.is_dir():
            steps.append(("worktree", "move", str(self.path), str(target.path)))
        if self.has(f"refs/heads/{self.branch}"):
            steps.append(("branch", "-m", self.branch, target.branch))
        if self.has(f"{TIPS_REF}/{self.name}"):
            steps += [("update-ref", f"{TIPS_REF}/{name}", self.git("rev-parse", f"{TIPS_REF}/{self.name}").stdout.strip()), ("update-ref", "-d", f"{TIPS_REF}/{self.name}")]
        for step in steps:
            moved = self.git(*step)
            if moved.returncode != 0:
                raise Rejection(f"the worktree {self.name} could not be renamed to {name}: {moved.stderr.strip()}")
        return target

    def local_branch(self) -> str:
        return self.run_git("rev-parse", "HEAD").stdout.strip()

    # what must hold before git is asked for a worktree, each refused with its cause and what to do
    def project_check(self) -> None:
        if self.git("rev-parse", "--git-dir").returncode != 0:
            raise WorktreeFailure(self.name, f"{self.root} is neither a git repository nor a folder holding git repositories, so there is no branch to work on: run git init and make a first commit, or launch without --worktree")
        if not self.has("HEAD"):
            raise WorktreeFailure(self.name, "the project has no commit yet, so there is nothing to cut a worktree from: make a first commit, then launch again")

    def added(self) -> None:
        self.registration_dropped()
        if self.has(f"refs/heads/{self.branch}"):
            added = self.git("worktree", "add", str(self.path), self.branch)
        elif self.has(f"{TIPS_REF}/{self.name}"):
            added = self.git("worktree", "add", "-b", self.branch, str(self.path), f"{TIPS_REF}/{self.name}")
        else:
            added = self.git("worktree", "add", "-b", self.branch, str(self.path))
        if added.returncode != 0:
            self.registration_dropped()
            if self.path.exists():
                shutil.rmtree(self.path)
            raise WorktreeFailure(self.name, self.add_refusal(added.stderr.strip()))

    def add_refusal(self, error: str) -> str:
        if "already checked out" in error or "already used by worktree" in error:
            return f"its branch {self.branch} is checked out in another folder (git worktree list names it): switch that folder to another branch, or launch with another --worktree name"
        return error.splitlines()[-1] if error else "git refused it without saying why"

    # git's record of this worktree alone, when its folder is gone; a prune would drop every other launch's whose folder is briefly away
    def registration_dropped(self) -> None:
        if self.is_registered():
            self.git("worktree", "remove", "--force", str(self.path))

    def uncommitted(self) -> list[str]:
        return [line[3:] for line in self.run_git("status", "--porcelain").stdout.splitlines() if line.strip()]

    def removed(self) -> None:
        self.record_tip()
        removal = self.git("worktree", "remove", str(self.path))
        if removal.returncode != 0:
            raise Rejection(f"the worktree {self.name} could not be removed: {removal.stderr.strip()}")

    # a worktree outlives its environment: deleting the environment keeps it, and only the person removes it
    def worktree_note(self) -> str:
        if not self.path.is_dir():
            return ""
        return f"its worktree {self.path} stays, as a worktree is never removed with its environment; journal worktree remove {self.name} removes it once its work is done"

    def is_registered(self) -> bool:
        listed = self.git("worktree", "list", "--porcelain").stdout.splitlines()
        return self.path.resolve() in {Path(line.removeprefix("worktree ")).resolve() for line in listed if line.startswith("worktree ")}

    def shared(self) -> None:
        wanted = [Path(JOURNAL), *self.untracked(self.skills()), *self.ignored([Path(p) for p in IGNORED_COPIES if (self.root / p).exists()])]
        self.excluded([*wanted, *map(Path, LINKED_SETTINGS)])
        self.cleared(self.path / JOURNAL)
        for path in wanted:
            self.linked(self.path / path, self.root / path)

    def skills(self) -> list[Path]:
        return [Path(folder) / entry.name for folder in SKILL_FOLDERS if (self.root / folder).is_dir() for entry in sorted((self.root / folder).iterdir())]

    def untracked(self, paths: list[Path]) -> list[Path]:
        tracked = {Path(name).parts[:3] for name in self.git("ls-files", "-z", "--", *map(str, paths)).stdout.split("\0") if name} if paths else set()
        return [path for path in paths if path.parts[:3] not in tracked]

    def ignored(self, paths: list[Path]) -> list[Path]:
        matched = set(self.git("check-ignore", *map(str, paths)).stdout.splitlines()) if paths else set()
        return [path for path in paths if str(path) in matched]

    def excluded(self, paths: list[Path]) -> None:
        exclude = Path(self.root, self.git("rev-parse", "--git-common-dir").stdout.strip(), "info", "exclude")
        exclude.parent.mkdir(parents=True, exist_ok=True)
        prior = exclude.read_text() if exclude.is_file() else ""
        lines = [line for line in ("/.claude/worktrees/", *(f"/{path}" for path in paths)) if line not in prior.splitlines()]
        if lines:
            exclude.write_text(prior + ("" if prior.endswith("\n") or not prior else "\n") + "\n".join(lines) + "\n")

    def cleared(self, place: Path) -> None:
        if place.is_symlink() or not place.is_dir():
            return
        tracked = [name for name in self.run_git("ls-files", "-z", "--", JOURNAL).stdout.split("\0") if name]
        if tracked:
            self.run_git("update-index", "--skip-worktree", "--", *tracked)
        shutil.rmtree(place)

    @staticmethod
    def linked(place: Path, target: Path) -> None:
        if place.is_symlink() and place.resolve() == target.resolve():
            return
        if place.exists() and not place.is_symlink():
            return
        place.parent.mkdir(parents=True, exist_ok=True)
        recent = place.with_name(f".{place.name}.{os.getpid()}.link")
        recent.unlink(missing_ok=True)
        recent.symlink_to(target, target_is_directory=target.is_dir())
        os.replace(recent, place)

    def run_git(self, *args: str) -> subprocess.CompletedProcess:
        return self.answered(["git", "-C", str(self.path), *args])

    def has(self, ref: str) -> bool:
        return self.git("rev-parse", "--verify", "--quiet", ref).returncode == 0

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return self.answered(["git", "-C", str(self.root), *args])

    def answered(self, argv: list[str]) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(argv, capture_output=True, text=True, timeout=self.git_seconds)
        except subprocess.TimeoutExpired:
            raise WorktreeFailure(self.name, f"git gave no answer within {self.git_seconds:g} seconds: check that git works in {self.root} (a lock left in .git, a slow disk), then launch again") from None
