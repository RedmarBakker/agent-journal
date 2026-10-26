from enum import StrEnum


class AgentRole(StrEnum):
    """What an agent is: the environment's main agent, a worker the main agent sent, a verifier the journal sent to judge a dismissal, a reviewer the journal sent to review a worker's work, or a subagent an agent started in its own session."""

    MAIN = "main"
    WORKER = "worker"
    VERIFIER = "verifier"
    REVIEWER = "reviewer"
    SUBAGENT = "subagent"

    def is_helper(self) -> bool:
        return self in AgentRole.helpers()

    @property
    def reach_name(self) -> str:
        return f"{self.value}s"

    @staticmethod
    def helpers() -> tuple["AgentRole", ...]:
        return (AgentRole.WORKER, AgentRole.VERIFIER, AgentRole.REVIEWER, AgentRole.SUBAGENT)
