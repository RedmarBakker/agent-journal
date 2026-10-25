from journal.events.rows.worker_mention import WorkerMention
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
from journal.support.voice_key import VoiceKey


class WorkerChat:
    """A worker's own chat: what it is informed, shown in the chat of the agent that dispatched it as a message sent to it, and each block of text it writes, read from its transcript from where the last read stopped, as messages of its session in the workers' chat; nothing is read of a conversation another agent now holds, as when a worker's session was resumed as the main agent."""

    def __init__(self, messages: Messages, workers: Workers, providers: Providers, branch: WorkerBranch, agents: Agents) -> None:
        self.messages, self.workers, self.providers, self.branch, self.agents = messages, workers, providers, branch, agents

    def instruction(self, worker: Worker, text: str, actor: Actor) -> Message:
        return self.messages.save(Message(environment_id=worker.environment_id, author=Author.USER, text=text, session=worker.conversation() or None, agent_role=AgentRole.WORKER), actor)

    def sent(self, worker: WorkerMention, text: str, actor: Actor) -> Message:
        roles = self.agents.session_roles(worker.dispatcher) if worker.dispatcher else []
        message = Message.outgoing(worker.title(), text, worker.dispatcher, worker.ref())
        return self.messages.save(message.with_(agent_role=roles[0]) if roles else message, actor)

    def read(self, worker: Worker) -> Worker:
        if not worker.conversation() or self.is_agent_session(worker):
            return worker
        blocks = self.providers.lookup(worker.provider).authored_texts(self.branch.place(worker), worker.conversation(), worker.transcript_bytes)
        for i, text in enumerate(blocks.texts):
            self.turn(worker, text, VoiceKey.placed(worker.conversation(), worker.transcript_bytes, i))
        return worker if blocks.time == worker.transcript_bytes else self.workers.touch(worker, Actor.system(), transcript_bytes=blocks.time)

    def is_agent_session(self, worker: Worker) -> bool:
        return any(not role.is_sent() for role in self.agents.session_roles(worker.conversation()))

    def turn(self, worker: Worker, text: str, key: str) -> None:
        self.messages.recorded(Message(environment_id=worker.environment_id, author=Author.AGENT, text=text, session=worker.conversation(), agent_role=AgentRole.WORKER, idempotency=key), Actor.agent(worker.conversation()))

