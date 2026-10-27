from dataclasses import replace

from journal.support.chain import Chain
from journal.support.classification import Classification
from journal.support.command_classifier import CommandClassifier
from journal.support.part import Part


class CommandLines:
    """What a whole shell line does, read from its parts' classification, with whether the files it names are the project's code read from the disk after the table: a line whose every part is of a read kind, shown by its ends, one that reads the project's code and runs as written, one that writes only the project's code."""

    def __init__(self, classifier: CommandClassifier) -> None:
        self.classifier = classifier

    def is_read(self, line: str) -> bool:
        owned = self.owned(line)
        return bool(owned) and all(self.classifier.classify(part.text).is_read_kind for part in owned)

    def is_code_read(self, line: str) -> bool:
        owned = self.owned(line)
        return any(self.reads_code(part) for part in owned) and all(self.reads_code(part) or self.is_harmless(part, self.classifier.classify(part.text)) for part in owned)

    def is_code_write(self, line: str) -> bool:
        owned = self.owned(line)
        classified = [(part, self.classifier.classify(part.text)) for part in owned]
        return any(classification.is_write for _, classification in classified) and all(self.writes_code(part.text) if classification.is_write else classification.is_read or self.is_harmless(part, classification) for part, classification in classified)

    def part_with_code_read(self, part: Part) -> Part:
        return replace(part, reads_code=self.reads_code(part))

    def reads_code(self, part: Part) -> bool:
        classification = self.classifier.classify(part.text)
        return classification.is_read and part.names_project_code(classification.is_search)

    @staticmethod
    def is_harmless(part: Part, classification: Classification) -> bool:
        return classification.is_harmless or part.is_project_cd()

    def writes_code(self, text: str) -> bool:
        targets = self.classifier.target_paths(text) or [word for word in self.classifier.stage_arguments(text) if Part.is_project_path(word)]
        return bool(targets) and all(Part.is_code_target(target) for target in targets)

    @staticmethod
    def owned(line: str) -> list[Part]:
        return [part for part in Chain.parts(line) if part.recorded]
