from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Decision:
    """What the hook script tells the agent back: go on, stop, or go on and read this; a line raised twice for one answer is said once."""

    allowed: bool = True
    reason: str = ""
    context: str = ""

    @classmethod
    def refuse(cls, reason: str) -> "Decision":
        return cls(False, unique_lines(reason))

    @classmethod
    def allowed_with(cls, context: str) -> "Decision":
        return cls(True, "", unique_lines(context))

    def without(self, prompt_text: str) -> "Decision":
        return replace(self, context="\n".join(line for line in self.context.split("\n") if line and line not in prompt_text))

    def merged(self, counterpart: "Decision") -> "Decision":
        return Decision(self.allowed and counterpart.allowed, unique_lines("\n".join(r for r in (self.reason, counterpart.reason) if r)), unique_lines("\n".join(c for c in (self.context, counterpart.context) if c)))


def unique_lines(text: str) -> str:
    return "\n".join(dict.fromkeys(text.split("\n"))) if text else text
