import re

from journal.models.support.sequence_step import SequenceStep
from journal.support.command_part import CommandPart
from journal.support.tool_call import ToolCall

# a command a step's instructions name in backticks, up to the first placeholder
COMMAND_PATTERN = re.compile(r"`([^`<]+)")


class StepCalls:
    """What a tool call is to the step in hand: work that waits until the step is taken up (a write, or a run of anything but reading and journal commands; a subagent only reads, so its dispatch goes through), or a command the step's instructions name in backticks, which takes the step up."""

    @staticmethod
    def is_work(call: ToolCall) -> bool:
        return call.writes or (call.work == "running" and not call.is_journal)

    @staticmethod
    def is_step_command(step_text: str, parts: tuple[CommandPart, ...]) -> bool:
        step_commands = [command.strip() for command in COMMAND_PATTERN.findall(step_text) if command.strip()]
        return any(part.text.strip().startswith(command) for part in parts for command in step_commands)

    @staticmethod
    def allowed_words(step: SequenceStep) -> str:
        return f", and {', '.join(step.allowed_commands)}" if step.allowed_commands else ""
