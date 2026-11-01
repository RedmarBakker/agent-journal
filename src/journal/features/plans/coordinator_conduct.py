from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.nudge import Nudge
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_part import PlansPart
from journal.support.code_files import CodeFiles
from journal.features.workers.workers_nudges import WorkersNudges

DISPATCHES = ("journal worker dispatch", "journal worker send")


class CoordinatorConduct(Conduct):
    """The main agent's conduct while it coordinates plans through Plan agents: code edits and its own workers are refused, and a stop carries the status of every started plan."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if CodeFiles.has_code(event.call.edited_paths):
            return self.refuse(PlansNudges.COORDINATOR_WRITES_NO_CODE.create())
        if any(part.text.startswith(DISPATCHES) for part in event.call.parts):
            return self.refuse(PlansNudges.COORDINATOR_SENDS_NO_WORKER.create())
        return self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none(*plan_lines(event.data, event.time))


def plan_lines(data: FeatureData, moment: float) -> tuple[Nudge, ...]:
    started = data.part(PlansPart).started_plans
    return (WorkersNudges.STARTED_PLANS.create(plans="; ".join(plan.line(moment) for plan in started)),) if started else ()
