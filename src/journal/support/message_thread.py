from enum import StrEnum

from journal.support.agent_role import AgentRole


class MessageThread(StrEnum):
    """Which chat a message is in: the environment's main agent's, a worker's, a verifier's, a reviewer's or a subagent's own, or the people's side thread beside the chat, which no agent reads."""

    MAIN = "main"
    WORKER = "worker"
    VERIFIER = "verifier"
    REVIEWER = "reviewer"
    SUBAGENT = "subagent"
    PEOPLE = "people"

    @classmethod
    def agent_thread(cls, role: AgentRole) -> "MessageThread":
        return cls(role.value)
