import shlex

from journal.support.chain import Chain

PREFIX = "printf '%s\\n' "


class RefusalCommand:
    """The shell line a refused command is replaced with, which prints the journal's reason and nothing else: the journal's own words, never a run to record, judge or read."""

    @staticmethod
    def build(reason: str) -> str:
        return f"{PREFIX}{shlex.quote(reason)}"

    @staticmethod
    def is_refusal(line: str) -> bool:
        parts = Chain.self_parts(line)
        return len(parts) == 1 and parts[0].startswith(PREFIX)
