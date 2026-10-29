from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.workers.orchestrator_conduct import plan_lines
from journal.features.workers.states.soloing import DISPATCHES
from journal.support.code_files import CodeFiles


class CoordinatorConduct(Conduct):
    """The main agent's conduct while Plan agents replace the work modes, brought by its floor to every state above it: a write to code and a worker of its own are refused, since it runs plans through their Plan agents; a stop carries the status of every started plan and names a started plan that has not moved while another moves."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if CodeFiles.has_code(event.call.edited_paths):
            return self.refuse(PlansNudges.COORDINATOR_WRITES_NO_CODE.create())
        if any(part.text.startswith(DISPATCHES) for part in event.call.parts):
            return self.refuse(PlansNudges.COORDINATOR_SENDS_NO_WORKER.create())
        return self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none(*plan_lines(event.data, event.time, settings))
