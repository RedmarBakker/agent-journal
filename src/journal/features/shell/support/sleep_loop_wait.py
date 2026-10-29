from journal.engine.command_events import CommandEvents
from journal.features.shell.support.sleep_loop import SleepLoop
from journal.features.tasks.support.wait_targets import WaitTargets
from journal.support.caller import Caller


class SleepLoopWait:
    """A loop that only sleeps, run as the agent's wait on the script that ends it, as journal await --until would."""

    def __init__(self, targets: WaitTargets, events: CommandEvents) -> None:
        self.targets, self.events = targets, events

    def declared(self, loop: SleepLoop, caller: Caller) -> str:
        name = self.targets.polled_check(loop.script, loop.title, caller.actor)
        self.events.wait_declared(loop.title, name, caller)
        return f"waiting on {self.targets.title(name)}\n"
