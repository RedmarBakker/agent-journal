import subprocess

from journal.features.shell.shell_nudges import ShellNudges
from journal.engine.nudge import Nudge
from journal.features.shell.support.cap import Cap
from journal.features.shell.support.output_files import OutputFiles



class OutputShow:
    """What the agent sees of a part's output in the foreground, as the cap sets: whole for a line of journal commands or an output under the cap; a cut part's cut applied and shown, the whole stored and named by the same one line; half the characters from each end for a read past the cap, with a line naming the lines shown and the lines cut; and for any other output past the cap one line naming the output to read by its number, with its lines, its characters and the part it was loaded from, and a shorter line for each later part the output also contains. The lines naming a stored output are notes for the agent's next hook, never part of what the command printed."""

    def __init__(self, folder: OutputFiles, cap: Cap) -> None:
        self.folder, self.cap = folder, cap
        self.named = False
        self.notes: list[Nudge] = []

    def build(self, i: int) -> str:
        return "".join(self.shown(i, name) for name in ("out", "err"))

    def shown(self, i: int, name: str) -> str:
        path = self.folder.folder / f"{i}.{name}"
        if not path.is_file():
            return ""
        text = path.read_text(errors="replace")
        cut = self.folder.cut_command(i)
        if cut and name == "out":
            shortened = subprocess.run(["sh", "-c", cut], input=text, capture_output=True, text=True).stdout
            shown = shortened if len(shortened) <= self.cap.characters else shortened[-self.cap.characters:]
            return f"{shown.rstrip(chr(10))}\n{self.naming_line(i, text)}"
        if self.cap.is_whole() or len(text) <= self.cap.characters:
            return text
        if self.cap.is_ends():
            return self.ends(text)
        return self.naming_line(i, text)

    def naming_line(self, i: int, text: str) -> str:
        if self.named:
            self.notes.append(ShellNudges.OUTPUT_PART_STORED.create(n=self.folder.number(), part=i + 1, counts=self.counts(text)))
            return ""
        self.named = True
        part = f", part {i + 1}" if len(self.folder.kinds()) > 1 else ""
        self.notes.append(ShellNudges.OUTPUT_STORED.create(n=self.folder.number(), counts=self.counts(text), part=part))
        return ""

    def ends(self, text: str) -> str:
        half = self.cap.characters // 2
        head, tail = text[:half], text[-half:]
        lines, head_lines, tail_lines = self.line_count(text), head.count("\n"), tail.count("\n")
        number = self.folder.number()
        cut = f"{head_lines + 1}-{lines - tail_lines}"
        return f"{head}\n[journal] output {number}: lines {cut} of {lines} cut; journal output read {number} --lines {cut}\n{tail}"

    def counts(self, text: str) -> str:
        return f"{self.line_count(text)} lines"

    @staticmethod
    def line_count(text: str) -> int:
        return text.count("\n") + (1 if text and not text.endswith("\n") else 0)
