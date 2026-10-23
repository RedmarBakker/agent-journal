import time

from journal.features.seed import Seed
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor


class CutOffOutputs(Seed):
    """At boot, every command not ended was cut off with the server that ran it, in the foreground or moved to the background, since its chain ran inside that server: it is recorded as ended so, and its agent is told once, as any other end."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def run(self) -> None:
        for output in self.outputs.unended():
            self.outputs.save(output.interrupted(time.time()), Actor.system())
