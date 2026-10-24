from enum import StrEnum


class AgentRole(StrEnum):
    """Whose chat a message is in, and what an agent is: the environment's main agent's, a worker's the main agent sent, a verifier's the journal sent to judge a dismissal, a subagent's an agent started in its own session, or the people's side thread beside the chat, which no agent reads."""

    MAIN = "main"
    WORKER = "worker"
    VERIFIER = "verifier"
    SUBAGENT = "subagent"
    PEOPLE = "people"

    def is_sent(self) -> bool:
        return self in AgentRole.sent()

    @staticmethod
    def sent() -> tuple["AgentRole", ...]:
        return (AgentRole.WORKER, AgentRole.VERIFIER)
