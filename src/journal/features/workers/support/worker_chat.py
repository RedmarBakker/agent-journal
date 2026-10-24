from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.agent_role import AgentRole
from journal.models.author import Author
from journal.models.message import Message
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class WorkerChat:
    """A worker's own chat: what it is informed, and each block of text it writes, read from its transcript from where the last read stopped, as messages of its session in the chat of its own role, a worker's or a verifier's; nothing is read of a conversation another agent now holds, as when a worker's session was resumed as the main agent."""

    def __init__(self, messages: Messages, workers: Workers, providers: Providers, branch: WorkerBranch, agents: Agents) -> None:
        self.messages, self.workers, self.providers, self.branch, self.agents = messages, workers, providers, branch, agents

    def instruction(self, worker: Worker, text: str, actor: Actor) -> Message:
        return self.messages.save(Message(environment_id=worker.environment_id, author=Author.USER, text=text, session=worker.conversation() or None, agent_role=self.chat_role(worker)), actor)

    def read(self, worker: Worker) -> Worker:
        if not worker.conversation() or self.is_agent_session(worker):
            return worker
        blocks = self.providers.lookup(worker.provider).authored_texts(self.branch.place(worker), worker.conversation(), worker.transcript_bytes)
        for i, text in enumerate(blocks.texts):
            self.turn(worker, text, f"transcript:{worker.conversation()}:{worker.transcript_bytes}:{i}")
        return worker if blocks.time == worker.transcript_bytes else self.workers.touch(worker, Actor.system(), transcript_bytes=blocks.time)

    def is_agent_session(self, worker: Worker) -> bool:
        return any(not role.is_sent() for role in self.agents.session_roles(worker.conversation()))

    def turn(self, worker: Worker, text: str, key: str) -> None:
        if self.messages.sent_with(key):
            return
        self.messages.save(Message(environment_id=worker.environment_id, author=Author.AGENT, text=text, session=worker.conversation(), agent_role=self.chat_role(worker), idempotency=key), Actor.agent(worker.conversation()))

    def chat_role(self, worker: Worker) -> AgentRole:
        return next(iter(self.agents.sent_roles(worker.conversation())), AgentRole.WORKER) if worker.conversation() else AgentRole.WORKER
