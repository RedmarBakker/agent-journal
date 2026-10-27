import json
import re

from journal.models.entry import Entry
from journal.models.subagent import Subagent
from journal.models.subagent_state import SubagentState
from journal.repositories.entries import Entries
from journal.support.agent_message import AgentMessage
from journal.support.subagent_dispatch import SubagentDispatch
from journal.support.task_notification import TaskNotification
from journal.references import events

ENDS = frozenset({events.STOP, events.SESSION_STARTED, events.SESSION_ENDED})
TURN_FAILED = events.TURN_FAILED
SUBAGENT_KINDS = ENDS | {events.SUBAGENT_STARTED, events.SUBAGENT_ENDED, TURN_FAILED}
TOOL_MOMENTS = (events.TOOL_STARTING, events.TOOL_FINISHED, events.TOOL_FAILED)


class SubagentEntries:
    """The subagents an agent dispatched, paired from its session's entries: each dispatch, its answer, its start and end in the background, a message that runs it again, and the failed turn of the agent, such as on its usage limit, that cuts every running one off."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def running_mentioning(self, session: str, subject: str) -> int:
        return sum(1 for row in self.mentioning(session, subject) if row.is_running())

    def dispatches_mentioning(self, session: str, subject: str, start: float) -> list[Subagent]:
        return [row for row in self.mentioning(session, subject) if row.latest_start_at >= start]

    def mentioning(self, session: str, subject: str) -> list[Subagent]:
        matched = re.compile(rf"\b{re.escape(subject)}\b", re.IGNORECASE)
        return [row for row in self.rows(session) if matched.search(row.brief)]

    def rows(self, session: str) -> list[Subagent]:
        return self.paired(self.entries.dispatches(session))

    def dispatched(self, session: str, dispatch: str) -> Subagent:
        return next(row for row in self.rows(session) if row.dispatch == dispatch)

    def report(self, session: str, row: Subagent) -> str:
        ends = self.entries.subagent_ends(session, row.session) if row.session else []
        return ends[-1].data.get("last_assistant_message", "") if ends else ""

    def current_rows(self, session: str, moment: float) -> list[Subagent]:
        return [row for row in self.rows(session) if row.is_current(moment)]

    @staticmethod
    def is_dispatch_entry(entry: Entry) -> bool:
        return entry.entry_type in SUBAGENT_KINDS or (entry.entry_type in TOOL_MOMENTS and isinstance(entry.recorded_call().operation, (SubagentDispatch, AgentMessage)))

    @staticmethod
    def message_receiver(entry: Entry) -> str:
        if entry.entry_type != events.TOOL_STARTING:
            return ""
        operation = entry.recorded_call().operation
        return operation.receiver if isinstance(operation, AgentMessage) else ""

    @staticmethod
    def paired(dispatches) -> list[Subagent]:
        rows: list[Subagent] = []
        open_: dict[str, int] = {}
        background: dict[str, int] = {}
        unstarted: dict[str, int] = {}
        for e in dispatches:
            time = e.created_at.timestamp()
            if e.entry_type == TURN_FAILED:
                reason = f"cut off when the agent's turn failed: {e.data.get('error', '')}"
                for active in (open_, background, unstarted):
                    SubagentEntries.failed_rows(rows, active, reason, time)
                continue
            if e.entry_type in ENDS:
                SubagentEntries.stopped(rows, open_, time)
                if e.entry_type == events.SESSION_ENDED or (e.entry_type == events.SESSION_STARTED and e.data.get("source") != "compact"):
                    SubagentEntries.stopped(rows, background, time)
                    SubagentEntries.stopped(rows, unstarted, time)
                continue
            if e.entry_type == events.SUBAGENT_STARTED:
                SubagentEntries.started(rows, background, unstarted, e.data.get("agent_id", ""))
                continue
            if e.entry_type == events.SUBAGENT_ENDED:
                i = background.pop(e.data.get("agent_id", ""), None)
                if i is not None:
                    rows[i] = rows[i].finished(SubagentState.FINISHED, time)
                continue
            if e.entry_type == events.PROMPT_SUBMITTED:
                SubagentEntries.notified(rows, background, str(e.data.get("prompt", "")), time)
                continue
            operation = e.recorded_call().operation
            if isinstance(operation, AgentMessage):
                SubagentEntries.resumed(rows, background, operation, e.entry_type, time)
                continue
            if not isinstance(operation, SubagentDispatch) or e.data.get("refused"):
                continue
            use = e.data.get("tool_use_id", "")
            if e.entry_type == events.TOOL_STARTING:
                brief = operation.brief or ""
                rows.append(Subagent(environment_id=e.environment_id, dispatch=f"sub:{e.id}", dispatcher=e.data.get("session_id", ""), started_at=time, task=operation.title or brief[:80], brief=f"{operation.title} {brief}", agent_type=operation.role or "subagent", model=operation.model))
                open_[use or f"entry:{e.id}"] = len(rows) - 1
            elif e.entry_type == events.TOOL_FAILED and open_:
                i = open_.pop(use) if use in open_ else open_.pop(next(iter(open_)))
                rows[i] = rows[i].failed(str(e.data.get("error", "")), time)
            elif e.entry_type == events.TOOL_FINISHED and open_:
                i = open_.pop(use) if use in open_ else open_.pop(next(iter(open_)))
                answer = SubagentEntries.answered(e.data.get("tool_response"))
                rows[i] = rows[i].answered(answer.get("agentId", ""))
                background_run = answer.get("isAsync") or operation.background
                if background_run and rows[i].session:
                    background[rows[i].session] = i
                elif operation.background:
                    unstarted[f"row:{i}"] = i
                else:
                    rows[i] = rows[i].finished(SubagentState.FINISHED, time)
        return rows

    @staticmethod
    def moved(row: Subagent, entry: Entry) -> Subagent:
        time, agent_id = entry.created_at.timestamp(), entry.data.get("agent_id", "")
        operation = entry.recorded_call().operation if entry.entry_type == events.TOOL_STARTING else None
        if isinstance(operation, AgentMessage) and operation.receiver == row.session:
            return row.resumed(time, operation.text)
        if not row.is_running():
            return row
        if entry.entry_type == events.SUBAGENT_ENDED and agent_id == row.session:
            return row.finished(SubagentState.FINISHED, time)
        if entry.entry_type == events.SESSION_ENDED or (entry.entry_type == events.SESSION_STARTED and entry.data.get("source") != "compact"):
            return row.finished(SubagentState.STOPPED, time)
        return row

    @staticmethod
    def notified(rows: list[Subagent], background: dict[str, int], prompt: str, time: float) -> None:
        for notification in TaskNotification.parsed(prompt):
            i = background.pop(notification.task_id, None)
            if i is None:
                i = next((n for n, row in enumerate(rows) if row.session == notification.task_id and row.state in (SubagentState.ACTIVE, SubagentState.FINISHED)), None)
            finished = i is not None and rows[i].state == SubagentState.FINISHED
            if i is not None and notification.is_change(finished):
                rows[i] = rows[i].notified(notification, rows[i].ended_at if finished else time)

    @staticmethod
    def started(rows: list[Subagent], background: dict[str, int], unstarted: dict[str, int], agent_id: str) -> None:
        if not unstarted or not agent_id:
            return
        i = unstarted.pop(next(iter(unstarted)))
        rows[i] = rows[i].answered(agent_id)
        background[agent_id] = i

    @staticmethod
    def resumed(rows: list[Subagent], background: dict[str, int], message: AgentMessage, type_name: str, time: float) -> None:
        if type_name != events.TOOL_STARTING:
            return
        for i in [i for i, row in enumerate(rows) if row.session and row.session == message.receiver]:
            rows[i] = rows[i].resumed(time, message.text)
            background[message.receiver] = i

    @staticmethod
    def failed_rows(rows: list[Subagent], active: dict[str, int], reason: str, time: float) -> None:
        for i in active.values():
            rows[i] = rows[i].failed(reason, time)
        active.clear()

    @staticmethod
    def stopped(rows: list[Subagent], active: dict[str, int], time: float) -> None:
        for i in active.values():
            rows[i] = rows[i].finished(SubagentState.STOPPED, time)
        active.clear()

    @staticmethod
    def answered(response) -> dict:
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                return {}
        return response if isinstance(response, dict) else {}
