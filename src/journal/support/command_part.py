from dataclasses import dataclass

from journal.support.classification import VERSION_CONTROL, Classification
from journal.support.command_classifier import CommandClassifier


@dataclass(frozen=True)
class CommandPart:
    """One command of a shell line as the journal read it before it ran: its text, whether it is a journal command, whether it writes and the files it will write or print, both read from its classification, whether it reads a stored output by hand, with the shape of that read, the output's number removed, so two reads of the same kind look alike, what the command table classifies it as, and its shape, the program and subcommands a run of it is known by."""

    text: str
    is_journal: bool
    writes: bool
    files: tuple[str, ...]
    reads_output: bool
    read_shape: str
    classification: Classification = Classification()
    shape: str = ""

    @classmethod
    def read(cls, text: str, is_journal: bool, reads_output: bool, read_shape: str, classifier: CommandClassifier) -> "CommandPart":
        classification = classifier.classify(text)
        files = classifier.target_paths(text) if classification.is_write else classifier.read_paths(text)
        return cls(text=text, is_journal=is_journal, writes=classification.is_write, files=files, reads_output=reads_output, read_shape=read_shape, classification=classification, shape=classifier.shape(text))

    @classmethod
    def parsed(cls, data: dict) -> "CommandPart":
        return cls(text=data.get("text", ""), is_journal=bool(data.get("is_journal")), writes=bool(data.get("writes")), files=tuple(data.get("files", ())),
                   reads_output=bool(data.get("reads_output")), read_shape=data.get("read_shape", ""), classification=Classification.parsed(data.get("classification", {})), shape=data.get("shape", ""))

    @property
    def is_folder_change(self) -> bool:
        return self.text.split()[:1] == ["cd"]

    @property
    def journal_noun(self) -> str:
        tokens = self.text.split()
        return tokens[1] if self.is_journal and len(tokens) > 1 else ""

    @property
    def is_git(self) -> bool:
        return self.classification.kind == VERSION_CONTROL
