from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.client_errors_part import ClientErrorsPart


class ClientErrorsConduct(Conduct):
    """The client errors feature's conduct in every state: while viewer errors stay unhandled, the agent is reminded of them at a tool use fifty after it was last told, never more often."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        errors = event.data.part(ClientErrorsPart)
        return self.none(ClientErrorsNudges.UNHANDLED.create(errors=ClientErrorsNudges.errors(errors.count))) if errors.count and not errors.is_reported else self.none()
