
from journal.features.registry import Registry
from journal.support.chain import Chain

JOURNAL = "journal"


class BackgroundCommands:
    """Whether a line runs a journal command that its feature's command names among its background verbs, such as worker merge: one that goes to the background at once, recorded and shown as any other command, where every other journal command stays in the foreground and is shown whole."""

    def __init__(self, registry: Registry) -> None:
        self.registry = registry

    def is_background(self, line: str) -> bool:
        return any(self.is_background_command(arguments[1:]) for part in Chain.self_parts(line) if (arguments := part.split())[:1] == [JOURNAL])

    def is_background_command(self, arguments: list[str]) -> bool:
        verb = arguments[2:3] if arguments[1:2] and arguments[1].isdigit() else arguments[1:2]
        return bool(arguments) and bool(verb) and self.registry.is_background_verb(arguments[0], verb[0])
