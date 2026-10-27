from dataclasses import dataclass


@dataclass(frozen=True)
class HookVerdict:
    """Whether a hook's answer let the action through, read as each provider's answer says it."""

    REFUSED = {
        "claude": lambda body: body.get("decision") == "block" or body.get("hookSpecificOutput", {}).get("permissionDecision") == "deny",
        "codex": lambda body: body.get("decision") == "block" or "error" in body,
    }

    provider: str
    status: int
    body: dict

    def refused(self) -> bool:
        return self.status == 409 or self.REFUSED[self.provider](self.body)
