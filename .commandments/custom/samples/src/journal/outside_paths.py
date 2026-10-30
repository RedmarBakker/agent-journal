import tempfile
from pathlib import Path


class CacheFolder:
    """A sample for the paths outside the project: a folder in the home, a ~ path, the system's temporary folder and a /tmp path, and the one under the project's .journal folder."""

    def __init__(self, journal_home: Path) -> None:
        self.journal_home = journal_home

    def home_folder(self) -> Path:
        # @sin PathOutsideProjectDetector
        return Path.home() / ".cache"

    def tilde_folder(self) -> Path:
        # @sin PathOutsideProjectDetector
        # @sin PathLiteralOutsideProjectDetector
        return Path("~/cache").expanduser()

    def scratch_folder(self) -> Path:
        # @sin PathOutsideProjectDetector
        return Path(tempfile.mkdtemp())

    def fixed_folder(self) -> Path:
        # @sin PathLiteralOutsideProjectDetector
        return Path("/tmp/journal-cache")

    def project_folder(self) -> Path:
        # @righteous PathOutsideProjectDetector
        return Path(tempfile.mkdtemp(dir=self.journal_home / "runtime"))
