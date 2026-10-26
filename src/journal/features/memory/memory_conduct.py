import re

from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent.stop import Stop
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.rule_created import RuleCreated
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_started import TaskStarted
from journal.models.memory_trigger import MemoryTrigger
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_options import MemoryOptions
from journal.features.memory.memory_part import MemoryPart
from journal.features.memory.memory_thresholds import MemoryThresholds


COMPACT = "compact"


class MemoryConduct(Conduct):
    """The memory feature's conduct in every state: at a context mark not taken yet the agent is instructed to decide what to keep, a write and a stop are blocked until it has, a fact, rule or reminder whose keyword comes up in what it writes or runs is typed back to it, a rule the agent made is questioned once, a reminder set for a moment is informed once its moment has come, at the first event after it or at the next session start, and one with a trigger is informed when its trigger fires while its condition holds."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        stale = event.data.part(MemoryPart).stale
        if event.source == COMPACT or not stale:
            return self.none()
        return self.none(MemoryNudges.CHECK_STALE_MEMORY.create(stale_after=settings.value(MemoryOptions.STALENESS_LIMIT), stale=", ".join(stale)))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if not event.call.writes or not event.data.part(MemoryPart).threshold_due:
            return self.none()
        return self.refuse(MemoryNudges.DECISION_EDIT_BLOCK.create())

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        obligations = event.data.part(MemoryPart).threshold_due
        return self.refuse(MemoryNudges.UNDECIDED_STOP.create(percent=obligations)) if obligations else self.none()

    def on_agent_event(self, event: AgentEvent, settings: Settings) -> Transition:
        return Transition.merged(self, [hint_check(self, event, settings), threshold_check(self, event, settings), self.none(*due_lines(event))])

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        return self.none(*triggered_lines(event, MemoryTrigger.TASK_COMPLETED)) if event.outcome == "completed" else self.none()

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        return self.none(*triggered_lines(event, MemoryTrigger.TASK_STARTED))

    def on_rule_created(self, event: RuleCreated, settings: Settings) -> Transition:
        return self.none(MemoryNudges.RULE_SCOPE_QUESTION.create(n=event.row_id)) if event.agent_origin else self.none()


def triggered_lines(event, trigger: MemoryTrigger) -> list:
    return [MemoryNudges.MEMORY_TRIGGERED.create(noun=row.noun, n=row.id, single_use=int(row.is_single_use)) for row in event.data.part(MemoryPart).triggered if row.trigger == trigger and row.ready]


def due_lines(event: AgentEvent) -> list:
    if isinstance(event, LineDelivered):
        return []
    return [MemoryNudges.REMINDER_DUE.create(n=reminder.id, text=reminder.text) for reminder in event.data.part(MemoryPart).timed if reminder.due_at <= event.time]



def threshold_check(state: BaseState, event: AgentEvent, settings: Settings) -> Transition:
    if event.context is None or not event.session:
        return state.none()
    threshold = MemoryThresholds.due(event.context, event.data.part(MemoryPart).context_threshold)
    return state.none(MemoryNudges.CONTEXT_DECISION.create(percent=threshold)) if threshold else state.none()


def hint_check(state: BaseState, event: AgentEvent, settings: Settings) -> Transition:
    if not event.content:
        return state.none()
    terms = set(re.findall(r"[a-z][a-z0-9_-]*", event.content.lower()))
    rows = [row for row in event.data.part(MemoryPart).rows if terms & set(row.keywords) and not row.presence]
    return state.none().typing(*(MemoryNudges.MEMORY_READ_REQUEST.create(noun=row.noun, n=row.id) for row in rows))
