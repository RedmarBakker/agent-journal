from journal.engine.job import Job
from journal.events.announcer import Announcer
from journal.events.moments.output_view_changed import OutputViewChanged
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class RunCardStart(Job):
    """Every second a watched run still going that has run 3 seconds and shows no card yet is announced as changed, so its card comes into the chat."""

    interval_seconds = 1.0

    def __init__(self, outputs: CommandOutputs, card: OutputProcessCard, announcer: Announcer, scope: Scope) -> None:
        self.outputs, self.card, self.announcer, self.scope = outputs, card, announcer, scope

    def tick(self, time: float) -> None:
        for output in self.outputs.running_watched():
            with self.scope.environment(output.environment_id):
                if output.has_run_long(time) and not self.card.is_shown(output):
                    self.announcer.announce(OutputViewChanged(environment_id=output.environment_id, output=output.row_id))
