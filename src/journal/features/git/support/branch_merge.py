import subprocess
from pathlib import Path


GIT_TIMEOUT_SECONDS = 30


class BranchMerge:
    """Checks and merges one branch into a project's current branch."""

    def refusal(self, checkout: Path, tip: str, label: str, prefix: str = "", untracked_advice: str = "take them out of its branch or move the checkout's copies aside, and merge again") -> str:
        if self.git("rev-parse", "--verify", "-q", f"{tip}^{{commit}}", cwd=checkout).returncode != 0:
            return f"its branch tip is no longer a commit in {label}"
        if self.git("symbolic-ref", "-q", "HEAD", cwd=checkout).returncode != 0:
            return f"{label} is on no branch, a detached head"
        if self.git("rev-parse", "--verify", "-q", "MERGE_HEAD", cwd=checkout).returncode == 0:
            return f"a merge is already in progress in {label}"
        if not self.git("config", "user.name", cwd=checkout).stdout.strip() or not self.git("config", "user.email", cwd=checkout).stdout.strip():
            return f"git has no user.name and user.email in {label}, which a merge needs"
        changed = self.git("diff", "--name-only", f"HEAD...{tip}", cwd=checkout)
        if changed.returncode != 0:
            return f"git could not compare its branch with {label}: {self.reason(changed)}"
        overlap = sorted(self.path(name, prefix) for name in set(changed.stdout.split()) & set(self.status_files(checkout)))
        if overlap:
            return f"you have uncommitted changes to files they change: {', '.join(overlap)}"
        untracked = self.untracked(checkout, tip, prefix)
        return f"its branch adds {', '.join(untracked)}, which lie untracked in {label}: {untracked_advice}" if untracked else ""

    def untracked(self, checkout: Path, tip: str, prefix: str = "") -> list[str]:
        added = self.git("diff", "--name-only", "--diff-filter=A", f"HEAD...{tip}", cwd=checkout).stdout.split()
        if not added:
            return []
        files = self.git("ls-files", "--others", "--exclude-standard", "--", *added, cwd=checkout).stdout.split()
        return sorted(self.path(name, prefix) for name in files)

    def status_files(self, checkout: Path) -> list[str]:
        entries = iter(self.git("status", "--porcelain=v1", "-z", cwd=checkout).stdout.split("\0"))
        files = []
        for entry in filter(None, entries):
            files.append(entry[3:])
            if entry[0] in "RC":
                next(entries, "")
        return files

    def merged(self, checkout: Path, tip: str) -> str:
        merged = self.git("merge", "--no-edit", tip, cwd=checkout)
        if merged.returncode == 0:
            return ""
        clashing = ", ".join(self.git("diff", "--name-only", "--diff-filter=U", cwd=checkout).stdout.split()) or self.reason(merged)
        self.git("merge", "--abort", cwd=checkout)
        return clashing

    def git(self, *arguments: str, cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *arguments], cwd=cwd, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS)

    @staticmethod
    def path(name: str, prefix: str) -> str:
        return f"{prefix}/{name}" if prefix else name

    @staticmethod
    def reason(result: subprocess.CompletedProcess) -> str:
        return (result.stderr.strip().splitlines() or ["git refused without saying why"])[-1]
