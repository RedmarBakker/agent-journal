from dataclasses import dataclass


@dataclass(frozen=True)
class CodexStatusUpdate:
    """The status fields one record of a Codex session's rollout carries, each absent where the record says nothing of it."""

    model: str | None = None
    effort: str | None = None
    context_tokens: int | None = None
    used_tokens: int | None = None

    @classmethod
    def parsed(cls, record: dict) -> "CodexStatusUpdate":
        payload = record.get("payload", {})
        if record.get("type") == "turn_context":
            return cls(model=payload.get("model"), effort=payload.get("effort"))
        if record.get("type") == "token_usage_record":
            return cls(used_tokens=payload.get("usage", {}).get("total_tokens"))
        if record.get("type") != "event_msg" or payload.get("type") != "token_count" or not isinstance(payload.get("info"), dict):
            return cls()
        usage = payload["info"]
        return cls(context_tokens=usage.get("model_context_window"), used_tokens=usage.get("last_token_usage", {}).get("total_tokens"))
