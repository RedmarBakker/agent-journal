import io
import subprocess
import tarfile
from pathlib import Path

from journal.config import Config
from journal.features.organization.support.revision_unreadable import RevisionUnreadable
from journal.support.inner_repositories import InnerRepositories

ARCHIVE_SECONDS = 60


class ContractRevision:
    """The organization folder as it was at a git version: its files are extracted once into a folder of their own named by the commit, so reading a version never touches the checked-out files."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def extracted(self, folder: Path, ref: str) -> Path:
        commit = InnerRepositories.git(folder, "rev-parse", "--verify", f"{ref}^{{commit}}")
        if commit.returncode != 0:
            raise RevisionUnreadable(f"The version {ref} is not a commit of the repository holding {folder}; name a branch, a tag or a commit, or clear the version")
        sha = commit.stdout.strip()
        target = self.config.home / "organization" / sha[:12]
        if not target.is_dir():
            self.extract(folder, sha, target)
        return target

    def extract(self, folder: Path, sha: str, target: Path) -> None:
        prefix = InnerRepositories.git(folder, "rev-parse", "--show-prefix").stdout.strip().rstrip("/")
        archive = subprocess.run(["git", "-C", str(folder), "archive", "--format=tar", f"{sha}:{prefix}" if prefix else sha], capture_output=True, timeout=ARCHIVE_SECONDS)
        if archive.returncode != 0:
            raise RevisionUnreadable(f"The version {sha[:12]} holds no {folder.name} folder: {archive.stderr.decode(errors='replace').strip()}")
        target.mkdir(parents=True)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(target, filter="data")
