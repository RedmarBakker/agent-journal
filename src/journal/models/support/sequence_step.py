import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SequenceStep:
    """One step of a sequence: its title, the instructions the agent is given, and its guards: whether file edits wait while it is in hand, and the commands it lets through, patterns on the shell line; reads and journal commands always go through; and the moment that ends it by itself, such as plan.reviewed when the plan it is about has all its reviewers back."""

    title: str = ""
    instructions: str = ""
    file_edits_allowed: bool = True
    allowed_commands: tuple[str, ...] = ()
    ending_moment: str = ""

    @classmethod
    def parsed(cls, data: dict | str) -> "SequenceStep":
        if isinstance(data, str):
            return cls(instructions=data)
        return cls(str(data.get("title", "")), str(data.get("instructions", "")), bool(data.get("file_edits_allowed", True)), tuple(data.get("allowed_commands", ())), str(data.get("ending_moment", "")))

    def published(self) -> dict:
        return {**asdict(self), "allowed_commands": list(self.allowed_commands)}

    def heading(self) -> str:
        return self.title or self.instructions.split(".")[0][:80]

    def allows(self, command: str) -> bool:
        return any(re.search(pattern, command) for pattern in self.allowed_commands)
