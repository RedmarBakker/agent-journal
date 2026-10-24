from journal.engine.job import Job
from journal.events.announcer import Announcer
from journal.events.moments.output_view_changed import OutputViewChanged
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.support.output_views import OutputViews
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class WatchRefresh(Job):
    """Every second the card of each watched output and of each one still running in the background is read again from its files, whatever its agent does, so the chat shows it moving, here and in a colleague's copy, which has the card but never the output; a card whose view has not changed is left as it is."""

    interval_seconds = 1.0

    def __init__(self, outputs: CommandOutputs, views: OutputViews, card: OutputProcessCard, announcer: Announcer, scope: Scope) -> None:
        self.outputs, self.views, self.card, self.announcer, self.scope = outputs, views, card, announcer, scope

    def tick(self, time: float) -> None:
        for output in self.outputs.all_carded():
            with self.scope.environment(output.environment_id):
                if self.views.view(output) != self.card.card_view(output):
                    self.announcer.announce(OutputViewChanged(environment_id=output.environment_id, output=output.row_id))
