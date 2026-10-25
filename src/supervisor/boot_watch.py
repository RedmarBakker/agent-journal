import shutil
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SECONDS = 60.0
TRACEBACK = "Traceback (most recent call last):"
TRACEBACK_LINES = 8


@dataclass(frozen=True)
class BootWatch:
    """How the supervisor watches each boot of a service, as its launch file says in plain data: a service not well within a number of seconds, read from a file when it names one, is started again once; failing again it is started from the copy of its code kept at its last good boot, the lines saying what failed written to a notice file for the service to tell once it is up."""

    notice: str
    keep_source: str
    keep_copy: str
    fallback_command: list[str]
    seconds_file: str = ""
    seconds: float = DEFAULT_SECONDS

    def wait_seconds(self) -> float:
        path = Path(self.seconds_file) if self.seconds_file else None
        text = path.read_text().strip() if path is not None and path.is_file() else ""
        return float(text) if text.replace(".", "", 1).isdigit() else self.seconds

    def keep(self) -> None:
        copy = Path(self.keep_copy)
        fresh = copy.with_name(copy.name + ".new")
        shutil.rmtree(fresh, ignore_errors=True)
        shutil.copytree(self.keep_source, fresh, ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))
        shutil.rmtree(copy, ignore_errors=True)
        fresh.rename(copy)

    def has_copy(self) -> bool:
        return Path(self.keep_copy).is_dir()

    def tell(self, line: str) -> None:
        with Path(self.notice).open("a") as notice:
            notice.write(line.replace("\n", " ") + "\n")

    @staticmethod
    def last_traceback(log: Path) -> str:
        lines = log.read_text(errors="replace").splitlines() if log.is_file() else []
        starts = [n for n, line in enumerate(lines) if line.startswith(TRACEBACK)]
        return "\n".join(lines[starts[-1]:][-TRACEBACK_LINES:]) if starts else "its log holds no traceback"
