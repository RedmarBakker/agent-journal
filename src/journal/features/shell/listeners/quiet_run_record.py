from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.shell.support.silent_runs import SilentRuns
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor


class QuietRunRecord(AgentListener[Ticked]):
    """A background run of the agent's that has printed nothing for long enough is marked on its row at the tick, once, and the mark raises OutputQuiet, which tells the agent."""

    def __init__(self, silent: SilentRuns, outputs: CommandOutputs) -> None:
        self.silent, self.outputs = silent, outputs

    def handle(self, event: Ticked) -> None:
        for run in self.silent.running(event.session):
            output = self.outputs.find(run.output)
            if not output.is_quiet_named:
                self.outputs.save(output.quiet_named(event.time, run.quiet_seconds), Actor.system())
