from journal.features.shell.support.activity_label import ActivityLabel
from journal.support.chain import Chain

# the commands that keep only some of the lines piped into them, so a test run's reader never sees the rest
FILTERS = frozenset({"grep", "egrep", "fgrep", "rg", "head", "tail", "awk", "sed", "cut", "sort", "uniq", "wc"})
TESTING = "testing"


class PipedTestRun:
    """The filter a test run in a shell line is piped into, if any: its reader reads the run's own lines, which the filter takes away."""

    @classmethod
    def piped_filter(cls, line: str) -> str:
        for part in Chain.split(line):
            stages = cls.stages(part)
            if len(stages) > 1 and ActivityLabel.build(stages[0]) == TESTING:
                programs = [stage.split()[0] for stage in stages[1:] if stage.split()]
                filters = [program for program in programs if program in FILTERS]
                if filters:
                    return filters[0]
        return ""

    @staticmethod
    def stages(part: str) -> list[str]:
        stages, current, quote = [], "", ""
        for character in part:
            if quote:
                quote = "" if character == quote else quote
            elif character in "'\"":
                quote = character
            elif character == "|":
                stages.append(current)
                current = ""
                continue
            current += character
        return [stage.strip() for stage in [*stages, current]]
