from dataclasses import dataclass

from journal.features.health.support.bypass import HOOK, SHELL, Bypass
from journal.support.chain import Chain

# the shell commands a line names in full, and how much of each, before it counts the rest
SHOWN_COMMANDS = 3
COMMAND_CHARACTERS = 100


@dataclass(frozen=True)
class UncheckedWork:
    """What went through unchecked while the journal did not answer and the agent has not been told: how many hooks let the tool go on, and the shell commands that ran in the shell itself, unrecorded."""

    hooks: int = 0
    commands: tuple[str, ...] = ()

    @classmethod
    def read(cls, bypasses: list[Bypass]) -> "UncheckedWork":
        return cls(sum(1 for bypass in bypasses if bypass.bypass_type == HOOK), tuple(" && ".join(Chain.self_parts(bypass.subject)) for bypass in bypasses if bypass.bypass_type == SHELL))

    def is_empty(self) -> bool:
        return not self.hooks and not self.commands

    @staticmethod
    def counted(count: int, noun: str) -> str:
        return f"{count} {noun}{'' if count == 1 else 's'}"

    def kinds_text(self) -> str:
        hooks = f"{self.counted(self.hooks, 'hook')} let the tool go on unchecked" if self.hooks else ""
        commands = f"{self.counted(len(self.commands), 'shell command')} ran in the shell itself, unrecorded" if self.commands else ""
        return " and ".join(part for part in (hooks, commands) if part)

    def commands_text(self) -> str:
        shown = [command[:COMMAND_CHARACTERS] for command in self.commands[:SHOWN_COMMANDS]]
        hidden = len(self.commands) - SHOWN_COMMANDS
        return "; ".join([*shown, f"and {hidden} more"] if hidden > 0 else shown)
