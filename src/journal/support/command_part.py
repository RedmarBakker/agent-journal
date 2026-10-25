from dataclasses import dataclass

from journal.support.part import Part


@dataclass(frozen=True)
class CommandPart:
    """One command of a shell line as the journal read it before it ran: its text, whether it is a journal command, whether it writes, the files it will touch, write or print, and whether it reads a stored output by hand, with the shape of that read, the output's number removed, so two reads of the same kind look alike."""

    text: str
    is_journal: bool
    writes: bool
    files: tuple[str, ...]
    reads_output: bool
    read_shape: str

    @classmethod
    def parsed(cls, data: dict) -> "CommandPart":
        return cls(text=data.get("text", ""), is_journal=bool(data.get("is_journal")), writes=bool(data.get("writes")), files=tuple(data.get("files", ())),
                   reads_output=bool(data.get("reads_output")), read_shape=data.get("read_shape", ""))

    @property
    def is_folder_change(self) -> bool:
        return self.text.split()[:1] == ["cd"]

    @property
    def journal_noun(self) -> str:
        tokens = self.text.split()
        return tokens[1] if self.is_journal and len(tokens) > 1 else ""

    @property
    def is_git(self) -> bool:
        return Part(self.text).program() == "git"
