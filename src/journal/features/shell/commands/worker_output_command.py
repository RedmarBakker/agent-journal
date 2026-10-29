from journal.features.shell.commands.output_command import OutputCommand
from journal.models.command_output import CommandOutput
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class WorkerOutputCommand(OutputCommand):
    """journal output as a worker runs it: it reads and lists only the outputs of its own commands."""

    def owned(self, n: int, caller: Caller) -> CommandOutput:
        output = self.outputs.find(n)
        if output.creator != caller.actor:
            raise Rejection(f"output {n} is not worker {caller.worker_number}'s: a worker reads only the outputs of its own commands")
        return output

    def page(self, last: int, caller: Caller) -> list[CommandOutput]:
        return self.outputs.page(last, creator=caller.actor)
