from journal.events.agent.command_ended import CommandEnded
from journal.events.agent_listener import AgentListener
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor


class OutputNotice(AgentListener[CommandEnded]):
    """A command that ended in the background is marked reported, and its watch ended, at the event the shell conduct named it from, so no ending is marked without its line."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def handle(self, event: CommandEnded) -> None:
        output = self.outputs.find(event.output)
        self.outputs.save(output.announced().unwatched() if output.is_watched else output.announced(), Actor.system())
