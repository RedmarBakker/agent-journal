import json
import os
import re
import shutil
import signal
from dataclasses import asdict
from itertools import islice
from pathlib import Path

from journal.support.command_classifier import CommandClassifier
from journal.support.part import Part
from journal.support.process_check import ProcessCheck
from journal.support.command_part import CommandPart

BLOCK_BYTES = 65536
STYLE_CODES = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


class OutputFiles:
    """An output's folder as the runner writes and reads it: the line and its parts, what each printed, how each ended, its number, and whether the chain is done or moved to the background."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def shell_started(self, pid: int) -> None:
        (self.folder / "pid").write_text(str(pid))

    def shell_pid(self) -> int:
        path = self.folder / "pid"
        return int(path.read_text()) if path.is_file() and path.read_text().strip().isdigit() else 0

    def stop(self, reason: str) -> None:
        pid = self.shell_pid()
        if ProcessCheck.is_running(pid):
            os.killpg(pid, signal.SIGKILL)
        parts = self.recorded()
        if parts:
            with (self.folder / f"{parts[-1]}.out").open("a") as stream:
                stream.write(f"\n{reason}\n")

    def is_stored(self) -> bool:
        return (self.folder / "parts").is_file()

    def recorded(self) -> list[int]:
        return [i for i, type_name in enumerate((self.folder / "parts").read_text().splitlines()) if type_name.startswith("R")]

    def lines(self) -> list[str]:
        return [STYLE_CODES.sub("", line) for path in self.parts() for line in path.read_text(errors="replace").splitlines()]

    def recorded_texts(self) -> list[tuple[int, str]]:
        return [(i, self.part_text(i)) for i in self.recorded()]

    def part_lines(self, parts: list[int]) -> list[str]:
        return [STYLE_CODES.sub("", line) for i in parts for line in self.output_text(i).splitlines()] if parts else self.lines()

    def line_count(self) -> int:
        return sum(self.counted(path) for path in self.parts())

    @staticmethod
    def counted(path: Path) -> int:
        count, last = 0, b"\n"
        with path.open("rb") as file:
            while block := file.read(BLOCK_BYTES):
                count, last = count + block.count(b"\n"), block[-1:]
        return count + (last != b"\n")

    def page(self, start: int, size: int) -> list[str]:
        rows, skipped = [], 0
        for path in self.parts():
            if len(rows) >= size:
                break
            line_count = self.counted(path)
            if skipped + line_count > start:
                first = max(0, start - skipped)
                with path.open(errors="replace", newline="\n") as file:
                    rows += [STYLE_CODES.sub("", line.rstrip("\r\n")) for line in islice(file, first, first + size - len(rows))]
            skipped += line_count
        return rows

    def last(self, n: int) -> list[str]:
        rows: list[str] = []
        for path in reversed(self.parts()):
            rows = self.tail(path, n - len(rows)) + rows
            if len(rows) >= n:
                break
        return rows[-n:]

    def parts(self) -> list[Path]:
        return [path for i in self.recorded() for name in (f"{i}.out", f"{i}.err") if (path := self.folder / name).is_file()]

    @staticmethod
    def tail(path: Path, n: int) -> list[str]:
        size, block = path.stat().st_size, BLOCK_BYTES
        with path.open("rb") as file:
            while True:
                start = max(0, size - block)
                file.seek(start)
                lines = file.read().decode(errors="replace").splitlines()
                if start == 0 or len(lines) > n:
                    return [STYLE_CODES.sub("", line) for line in lines[-n:]] if n > 0 else []
                block *= 4

    def statuses(self) -> list[int]:
        return [int(path.read_text()) for i in self.recorded() if (path := self.folder / f"{i}.status").is_file()]

    def is_running(self) -> bool:
        return not (self.folder / "done").is_file() and len(self.statuses()) < len(self.recorded())

    def outcome(self) -> str:
        completed = self.statuses()
        return "still running" if self.is_running() or not completed else self.ended(completed[-1])

    @staticmethod
    def ended(status: int) -> str:
        return "finished" if status == 0 else f"failed with code {status}"

    def split(self, line: str, parts: list[Part], classifier: CommandClassifier) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "line").write_text(line)
        commands = [CommandPart.plain(part.text, classifier) for part in parts]
        for i, (part, command) in enumerate(zip(parts, commands)):
            (self.folder / f"{i}.part").write_text(part.uncut().text)
            (self.folder / f"{i}.command").write_text(json.dumps(asdict(command)))
            if part.cut():
                (self.folder / f"{i}.cut").write_text(part.cut_command())
        (self.folder / "parts").write_text("".join(part.part_type() + self.flags(part, command) + "\n" for part, command in zip(parts, commands)))

    @staticmethod
    def flags(part: Part, command: CommandPart) -> str:
        classification = command.classification
        return ("w" if part.recorded and classification.is_write else "-") + ("b" if classification.changes_version_control else "-")

    def kinds(self) -> list[str]:
        return (self.folder / "parts").read_text().splitlines()

    def part_text(self, i: int) -> str:
        return (self.folder / f"{i}.part").read_text()

    def command_part(self, i: int) -> CommandPart:
        return CommandPart.parsed(json.loads((self.folder / f"{i}.command").read_text()))

    def cut_command(self, i: int) -> str:
        path = self.folder / f"{i}.cut"
        return path.read_text() if path.is_file() else ""

    def number(self) -> int:
        path = self.folder / "number"
        return int(path.read_text()) if path.is_file() else 0

    def numbered(self, number: int) -> None:
        (self.folder / "number").write_text(str(number))

    def has_ended(self, i: int) -> bool:
        return (self.folder / f"{i}.status").is_file()

    def status(self, i: int) -> int:
        return int((self.folder / f"{i}.status").read_text())

    def ended_with(self, i: int, status: int) -> None:
        (self.folder / f"{i}.status").write_text(str(status))

    def output_text(self, i: int) -> str:
        return "".join(path.read_text(errors="replace") for name in (f"{i}.out", f"{i}.err") if (path := self.folder / name).is_file())

    def is_finished(self) -> bool:
        return (self.folder / "done").is_file()

    def finish(self, status: int) -> None:
        (self.folder / "done").write_text(str(status))

    def is_moved(self) -> bool:
        return (self.folder / "moved").is_file()

    def moved(self) -> None:
        (self.folder / "moved").touch()

    def output_time(self) -> float:
        return max((path.stat().st_mtime for path in self.parts()), default=0.0)

    def size(self) -> int:
        return sum(path.stat().st_size for path in self.folder.glob("*.out")) + sum(path.stat().st_size for path in self.folder.glob("*.err"))

    def has_cut(self) -> bool:
        return any(self.folder.glob("*.cut"))

    def remove(self) -> None:
        shutil.rmtree(self.folder, ignore_errors=True)
