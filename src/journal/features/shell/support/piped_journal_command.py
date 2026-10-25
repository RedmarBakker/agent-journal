from journal.features.shell.support.piped_test_run import FILTERS, PipedTestRun
from journal.support.chain import Chain

JOURNAL = "journal"


class PipedJournalCommand:
    """The journal command of a shell line, among those whose verbs its commands declare uncut, that is piped into a filter, with the filter: what the journal says to the agent is read in full or not at all."""

    @classmethod
    def piped(cls, line: str, uncut_verbs: tuple[str, ...]) -> tuple[str, str] | None:
        for part in Chain.split(line):
            stages = PipedTestRun.stages(part.strip().removeprefix("(").removesuffix(")"))
            filters = [program for stage in stages[1:] if (program := stage.split()[0] if stage.split() else "") in FILTERS]
            command = cls.uncut_command(stages[0], uncut_verbs) if len(stages) > 1 else ""
            if command and filters:
                return command, filters[0]
        return None

    @staticmethod
    def uncut_command(stage: str, uncut_verbs: tuple[str, ...]) -> str:
        tokens = stage.split()
        if tokens[:1] != [JOURNAL] or len(tokens) < 3:
            return ""
        verb = tokens[3:4] if tokens[2].isdigit() else tokens[2:3]
        command = f"{tokens[1]} {verb[0]}" if verb else ""
        return command if command in uncut_verbs else ""
