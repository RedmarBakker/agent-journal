from enum import StrEnum


class AgentRole(StrEnum):
    """Whose chat a message is in, and what an agent is: the environment's main agent's, a worker's the main agent sent, a verifier's the journal sent to judge a dismissal, a reviewer's the journal sent to review a worker's work, a subagent's an agent started in its own session, or the people's side thread beside the chat, which no agent reads."""

    MAIN = "main"
    WORKER = "worker"
    VERIFIER = "verifier"
    REVIEWER = "reviewer"
    SUBAGENT = "subagent"
    PEOPLE = "people"

    def is_helper(self) -> bool:
        return self in AgentRole.helpers()

    @staticmethod
    def helpers() -> tuple["AgentRole", ...]:
        return (AgentRole.WORKER, AgentRole.VERIFIER, AgentRole.REVIEWER, AgentRole.SUBAGENT)
