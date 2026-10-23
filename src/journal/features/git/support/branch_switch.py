import shlex

from journal.support.tool_call import ToolCall

SWITCHING = ("checkout", "switch")
CREATING = ("-b", "-B", "-c", "-C", "--create", "--force-create", "--orphan")


class BranchSwitch:
    """The branch a shell command moves the checkout onto with git checkout or git switch, empty when it moves none, as a checkout of files after -- moves none."""

    @classmethod
    def call_target(cls, call: ToolCall) -> str:
        return next((branch for line in call.shell_lines() if (branch := cls.target(line))), "")

    @staticmethod
    def target(line: str) -> str:
        try:
            arguments = shlex.split(line)
        except ValueError:
            return ""
        if len(arguments) < 3 or arguments[0] != "git" or arguments[1] not in SWITCHING or "--" in arguments:
            return ""
        branches = [argument for argument in arguments[2:] if not argument.startswith("-") or argument in CREATING]
        if branches and branches[0] in CREATING:
            return branches[1] if len(branches) > 1 else ""
        return branches[0] if branches else ""
