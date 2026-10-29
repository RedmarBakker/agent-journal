from journal.events.worker_merge_result import WorkerMergeResult
from journal.events.worker_merging import WorkerMerging
from journal.events.moments.worker_merge_clash import WorkerMergeClash
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.support.decision import Decision
from journal.engine.clock import Clock
from journal.engine.support.agent_event_audience import AgentEventAudience
from journal.events.agent.wait_cleared import WaitCleared
from journal.events.agent.wait_request import WaitRequest
from journal.events.agent.command_ended import CommandEnded
from journal.events.agent.command_moved import CommandMoved
from journal.events.agent.impasse_report import ImpasseReport
from journal.events.agent.helper_assignment import HelperAssignment
from journal.engine.base_state import BaseState
from journal.events.bus import Bus
from journal.models.agent import Agent
from journal.models.command_output import CommandOutput
from journal.support.caller import AGENT_REQUIRED, Caller
from journal.support.rejection import Rejection


class CommandEvents:
    """The events a command or the runner raises, dispatched here as a hook's are, a helper's reaching only the listeners its file allows: a command moved to the background and a moved command's end, each by its output's number; a wait the agent declares; the agent reporting it is stuck; a helper given its job by the journal, a worker's merge about to happen, which a listener may block, its result, and its refusal on a clash."""

    def __init__(self, bus: Bus, audience: AgentEventAudience, clock: Clock) -> None:
        self.bus, self.audience, self.clock = bus, audience, clock

    def moved(self, output: CommandOutput, caller: Caller) -> None:
        agent = self.caller_agent(caller)
        self.audience.dispatch(CommandMoved(output=output.row_id, agent=agent).placed(agent, None, self.clock.time()))

    def ended(self, output: CommandOutput, agent: Agent) -> None:
        self.audience.dispatch(CommandEnded(output=output.row_id, status=output.status, agent=agent).placed(agent, None, self.clock.time()))

    def wait_declared(self, subject: str, end_refs: str, caller: Caller) -> None:
        agent = self.caller_agent(caller)
        self.audience.dispatch(WaitRequest(focus=subject, end_refs=end_refs, agent=agent).placed(agent, None, self.clock.time()))

    def wait_cleared(self, caller: Caller) -> None:
        agent = self.caller_agent(caller)
        self.audience.dispatch(WaitCleared(agent=agent).placed(agent, None, self.clock.time()))

    def helper_assigned(self, state: BaseState, agent: Agent) -> None:
        self.audience.dispatch(HelperAssignment(state=state, agent=agent).placed(agent, None, self.clock.time()))

    @staticmethod
    def caller_agent(caller: Caller) -> Agent:
        if not caller.has_agent_row():
            raise Rejection(AGENT_REQUIRED)
        return caller.agent_row

    def worker_merging(self, event: WorkerMerging) -> list[str]:
        return [answer.reason for answer in self.bus.dispatch(event) if isinstance(answer, Decision) and not answer.allowed]


    def worker_merge_result(self, event: WorkerMergeResult) -> None:
        self.bus.dispatch(event)

    def worker_work_merged(self, event: WorkerWorkMerged) -> None:
        self.bus.dispatch(event)

    def worker_merge_refused(self, event: WorkerMergeClash) -> None:
        self.bus.dispatch(event)

    def help_needed(self, reason: str, caller: Caller) -> None:
        agent = self.caller_agent(caller)
        self.audience.dispatch(ImpasseReport(reason=reason, agent=agent).placed(agent, None, self.clock.time()))
