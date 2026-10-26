from dataclasses import dataclass

from journal.providers.support.profile_type import ProfileType


@dataclass(frozen=True)
class Profile:
    """A worker or a subagent as each provider reads it: what it does, which tools it may use and what instructions it is given."""

    name: str
    description: str
    tools: str
    body: str
    kind: ProfileType = ProfileType.SUBAGENT
    model: str | None = None

    def model_default(self, selection: str) -> str:
        return selection if self.model is None else self.model

