import subprocess
from collections.abc import Callable
from pathlib import Path

from journal.config import Config

GIT_SECONDS = 10
LOCAL_SETTINGS = ".claude/settings.local.json"


class ProjectUpdateCommit:
    """Commits the journal-owned project changes from an update."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def commit(
        self,
        files: list[Path],
        release: str,
        managed_text: dict[Path, Callable[[str], str]],
    ) -> list[str]:
        paths = [path for path in self.pathspecs(files) if path != LOCAL_SETTINGS]
        if not release or not paths or self.git("rev-parse", "--show-toplevel").returncode:
            return []
        paths = self.present_or_tracked(paths)
        if not paths:
            return []
        originals: dict[str, bytes | None] = {}
        try:
            self.use_managed_text(paths, managed_text, originals)
            self.answered(self.git("add", "-f", "--", *paths))
            changed = self.changed(paths)
            if not changed:
                return []
            self.answered(self.git("commit", "--only", "-m", self.message(release), "--", *changed))
            return changed
        finally:
            self.restore(originals)

    def message(self, release: str) -> str:
        commit = self.installed_commit()
        suffix = f" at {commit[:7]}" if commit else ""
        return f"Update the journal to {release}{suffix}"

    def installed_commit(self) -> str:
        path = self.config.home / "src" / "commit"
        return path.read_text().strip() if path.is_file() else ""

    def use_managed_text(self, paths: list[str], transforms: dict[Path, Callable[[str], str]], originals: dict[str, bytes | None]) -> None:
        relative = {path.relative_to(self.config.root).as_posix(): transform for path, transform in transforms.items()}
        for path in paths:
            transform = relative.get(path)
            if transform is None:
                continue
            full = self.config.root / path
            originals[path] = full.read_bytes() if full.is_file() else None
            previous = self.git("show", f"HEAD:{path}")
            baseline = previous.stdout if previous.returncode == 0 else ""
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(transform(baseline))

    def present_or_tracked(self, paths: list[str]) -> list[str]:
        return [path for path in paths if (self.config.root / path).exists() or self.tracked(path)]

    def tracked(self, path: str) -> bool:
        return self.git("ls-files", "--error-unmatch", "--", path).returncode == 0

    def restore(self, originals: dict[str, bytes | None]) -> None:
        for path, content in originals.items():
            full = self.config.root / path
            if content is None:
                full.unlink(missing_ok=True)
            else:
                full.write_bytes(content)

    def pathspecs(self, files: list[Path]) -> list[str]:
        return sorted({path.relative_to(self.config.root).as_posix() for path in files})

    def changed(self, paths: list[str]) -> list[str]:
        result = self.answered(self.git("diff", "--cached", "--no-renames", "--name-only", "-z", "--", *paths))
        return sorted(path for path in result.stdout.split("\0") if path)

    def git(self, *arguments: str, given: str = "") -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.config.root), *arguments], input=given, capture_output=True, text=True, timeout=GIT_SECONDS)

    @staticmethod
    def answered(result: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "git refused the journal update commit")
        return result
