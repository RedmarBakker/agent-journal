from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.shell.support.activity_label import LONG_RUNS, ActivityLabel
from journal.features.shell.support.output_views import OutputViews
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor

TOTAL_WAIT_SECONDS = 60


class UntotaledRunRecord(AgentListener[Ticked]):
    """A watched test run or build of the agent's that has printed for a minute without its card showing how far it has come is marked on its row, once, and the mark raises OutputWithoutTotal, which tells the agent."""

    def __init__(self, outputs: CommandOutputs, views: OutputViews, labels: ActivityLabel) -> None:
        self.outputs, self.views, self.labels = outputs, views, labels

    def handle(self, event: Ticked) -> None:
        for output in self.outputs.watched(event.session):
            if self.is_untotaled(output, event.time):
                self.outputs.save(output.total_asked(event.time), Actor.system())

    def is_untotaled(self, output, time: float) -> bool:
        if output.ended or output.is_total_asked or time - output.creation_time.timestamp() < TOTAL_WAIT_SECONDS or self.labels.line_label(output.command) not in LONG_RUNS:
            return False
        view = self.views.view(output)
        return bool(view.lines) and not view.fraction
