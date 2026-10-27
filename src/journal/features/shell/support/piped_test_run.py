from journal.support.part import Part
from journal.models.alias import Alias
from journal.support.alias_call import AliasCall
from journal.support.chain import Chain
from journal.support.command_part import CommandPart

# the commands that keep only some of the lines piped into them, so a test run's reader never sees the rest
FILTERS = frozenset({"grep", "egrep", "fgrep", "rg", "head", "tail", "cat", "awk", "sed", "cut", "sort", "uniq", "wc"})


class PipedTestRun:
    """The filter a test run in a shell line is piped into, if any, the run being a part its classification calls a test run or an alias with a reader: its reader reads the run's own lines, which the filter takes away."""

    @classmethod
    def piped_filter(cls, parts: tuple[CommandPart, ...], aliases: dict[str, Alias]) -> str:
        for command, part in ((command, part) for part in parts for command in cls.parts(part.text)):
            stages = cls.stages(command)
            if len(stages) > 1 and cls.is_watched(stages[0], part, aliases):
                programs = [stage.split()[0] for stage in stages[1:] if stage.split()]
                filters = [program for program in programs if program in FILTERS]
                if filters:
                    return filters[0]
        return ""

    @classmethod
    def parts(cls, line: str) -> list[str]:
        return [inner for part in Chain.split(line) for inner in (cls.parts(part.strip()[1:-1]) if Part(part).is_subshell() else [part])]

    @staticmethod
    def is_watched(stage: str, part: CommandPart, aliases: dict[str, Alias]) -> bool:
        alias = aliases.get(AliasCall.parsed(stage).name)
        return part.classification.is_test_run or (alias is not None and bool(alias.reader))

    @staticmethod
    def stages(part: str) -> list[str]:
        return Part(part).stages()
