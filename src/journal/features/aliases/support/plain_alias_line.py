from journal.support.caller import Caller


class PlainAliasLine:
    """The arguments an alias runs with, as they were typed."""

    def argv(self, argv: list[str], caller: Caller) -> list[str]:
        return argv
