from journal.models.agent import Agent
from journal.models.reviewer import Reviewer
from journal.models.support.ref import Ref
from journal.models.verifier import Verifier
from journal.models.worker import Worker
from journal.repositories.workers import Workers
from journal.support.agent_role import AgentRole
from journal.support.caller import Caller
from journal.support.missing_row import MissingRow
from journal.support.rejection import Rejection

SUBAGENT_REFUSAL = "a subagent keeps no memories: its command names no row of its own, so it would reach its agent's"


class MemoryOwners:
    """Whose memories an agent or a command keeps: None for the environment's main agent, the user and a plugin, the row of the worker, verifier or reviewer that runs it, and none at all for a subagent, whose command names no row of its own."""

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def caller_owner(self, caller: Caller) -> Ref | None:
        if caller.subagent:
            raise Rejection(SUBAGENT_REFUSAL)
        numbers = ((Worker, caller.worker_number), (Verifier, caller.verifier_number), (Reviewer, caller.reviewer_number))
        return next((Ref(model.table(), number) for model, number in numbers if number is not None), None)

    def agent_owner(self, agent: Agent) -> Ref | None:
        if agent.role == AgentRole.MAIN:
            return None
        rows = self.workers.session_worker(agent.session)
        if not rows:
            raise MissingRow(Worker.table(), agent.session)
        return Ref.build(rows[0])
