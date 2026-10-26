from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor


class StoppedOutputEnd(AgentListener[Ticked]):
    """At each tick a command not ended whose heartbeat stopped is ended as cut off, so a command whose process vanished never lingers as running or holds a restart."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def handle(self, event: Ticked) -> None:
        for output in self.outputs.stopped_outputs():
            self.outputs.save(output.interrupted(event.time), Actor.system())
