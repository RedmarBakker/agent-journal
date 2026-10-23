from pathlib import Path

from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.worker import Worker

LOCKFILES = {
    "node_modules": ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb"),
    ".venv": ("uv.lock", "poetry.lock", "Pipfile.lock", "requirements.txt"),
    "vendor": ("composer.lock",),
}


class PoolLockfiles:
    """Whether the library folders a pool worker links on the machine that runs it were installed from the same lockfiles as its base: a folder whose lockfile beside it differs from the base's is the wrong set of libraries for that base."""

    def __init__(self, branch: WorkerBranch) -> None:
        self.branch = branch

    def differing(self, worker: Worker) -> list[str]:
        checkout = self.branch.checkout(worker)
        return [str(path) for library in worker.library_links for path in self.lockfiles(library) if self.is_different(checkout, worker.base, path)]

    @staticmethod
    def lockfiles(library: str) -> list[Path]:
        folder = Path(library)
        return [folder.parent / name for name in LOCKFILES.get(folder.name, ())]

    def is_different(self, checkout: Path, base: str, path: Path) -> bool:
        local = checkout / path
        based = self.branch.git("show", f"origin/{base}:{path.as_posix()}", cwd=checkout)
        if not local.is_file():
            return based.returncode == 0
        return based.returncode != 0 or based.stdout != local.read_text()
