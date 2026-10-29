from journal.engine.support.machine_reply import MachineReply
from journal.engine.support.typist import CLEAR, DISABLE, ENABLE, PAUSE, RESUME
from journal.events.agent.agent_event import AgentEvent
from journal.supervisor_link import SupervisorLink
from journal.support.decision import Decision


class Delivery:
    """The terminal's side of the state machine's replies, the engine's one way to the supervisor for them: the moves the states asked of the terminal as the stack is stored, the lines typed into it and the remarks queued for it, whether the agent works, rests or had its stop refused, the silence between hooks, and the lines still queued folded into a hook's answer."""

    def __init__(self, supervisor: SupervisorLink) -> None:
        self.supervisor = supervisor

    def silence(self, event: AgentEvent) -> None:
        self.supervisor.silence(event.environment_id, event.gap_seconds())

    def moved(self, environment_id: int, moves: list[str]) -> None:
        terminal_moves = {PAUSE: self.supervisor.pause, RESUME: self.supervisor.resume, DISABLE: self.supervisor.disable, ENABLE: self.supervisor.enable, CLEAR: self.supervisor.clear}
        for move in moves:
            terminal_moves[move](environment_id)

    def applied(self, reply: MachineReply, following: float) -> None:
        environment_id = reply.agent.environment_id
        for remark in reply.remarks:
            self.supervisor.remark(environment_id, remark)
        for line in reply.keystrokes:
            self.supervisor.type(environment_id, line, following=following)

    def lines(self, environment_id: int, lines: str, following: float) -> None:
        for line in lines.split("\n"):
            self.supervisor.type(environment_id, line, following=following)

    def hook_decision(self, event: AgentEvent, answered: Decision) -> Decision:
        if answered.context and not event.has_hook_lines():
            self.lines(event.environment_id, answered.context, event.typing_delay)
        decision = self.with_remarks(event, answered.without(event.journal_text()) if event.journal_text() else answered)
        stop_refusal = event.is_turn_end and not decision.allowed
        if event.is_turn_end and not stop_refusal:
            self.supervisor.resting(event.environment_id)
        if not event.is_work and not stop_refusal:
            return decision
        if stop_refusal:
            self.supervisor.stop_refused(event.environment_id)
        else:
            self.supervisor.working(event.environment_id)
        return self.with_lines(decision, self.line_backlog(event))

    def with_remarks(self, event: AgentEvent, decision: Decision) -> Decision:
        if event.is_work or not event.is_remark_carrier() or event.defers_remarks():
            return decision
        return self.with_lines(decision, self.supervisor.pending_remarks(event.environment_id))

    def line_backlog(self, event: AgentEvent) -> str:
        if event.is_remark_carrier():
            return self.supervisor.pending_lines(event.environment_id)
        return self.supervisor.pending_instructions(event.environment_id)

    @staticmethod
    def with_lines(decision: Decision, lines: str) -> Decision:
        if not lines:
            return decision
        return decision.merged(Decision.allowed_with(lines)) if decision.allowed else Decision.refuse("\n".join((decision.reason, lines)))
