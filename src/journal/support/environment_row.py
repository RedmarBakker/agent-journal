from dataclasses import dataclass, field


@dataclass(frozen=True)
class EnvironmentRow:
    """An environment as the boot menu lists it: whether an agent works in it, when it was last used, each agent program's newest session it can still carry on, why no agent may start in it, as in a colleague's environment on a shared journal, and whether it works in a worktree of its own."""

    name: str
    working: bool = False
    last_used: str = ""
    last_sessions: dict[str, str] = field(default_factory=dict)
    refusal: str = ""
    worktree: bool = False
    agent: str = ""
    agent_session: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "EnvironmentRow":
        return cls(**data)

    def last_session(self, agent: str) -> str:
        return self.last_sessions.get(agent, "")

    def badges(self) -> tuple[str, ...]:
        working = ("agent working",) if self.working else ()
        return (*working, f"last used {self.last_used}") if self.last_used else working
