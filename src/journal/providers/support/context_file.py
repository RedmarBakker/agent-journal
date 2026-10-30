import json
import math
from pathlib import Path

from journal.providers.support.agent_status import AgentStatus
from journal.providers.support.rate_window import RateWindow


class ContextFile:
    """What a program reports about a session through the journal's status script, not a hook: the script writes one file per session, Claude Code's status line feeds it and Codex has none, and this reads the latest complete one. The plan's limits belong to the account, so a session whose status line has not reported them yet shows the newest any session reported; a session read alone, as a Codex session is, shows only what it reported itself."""

    def __init__(self, home: Path) -> None:
        self.home = home
        self._whole: dict[str, dict] = {}

    def build(self, session: str) -> float | None:
        used = self.status(session).get("context_window", {}).get("used_percentage")
        return used / 100 if used is not None else None

    def status(self, session: str) -> dict:
        path = self.home / f"{session}.json"
        if not path.is_file():
            return {}
        try:
            self._whole[session] = json.loads(path.read_text() or "{}")
        except json.JSONDecodeError:
            return self._whole.get(session, {})
        return self._whole[session]

    def model(self, session: str) -> str:
        return self.status(session).get("model", {}).get("display_name", "")

    def estimated_cost(self, session: str) -> float | None:
        status = self.status(session)
        if status.get("session_id") != session:
            return None
        cost = status.get("cost")
        if not isinstance(cost, dict):
            return None
        amount = cost.get("total_cost_usd")
        return float(amount) if isinstance(amount, (int, float)) and not isinstance(amount, bool) and math.isfinite(float(amount)) and amount >= 0 else None

    def effort(self, session: str) -> str:
        return self.status(session).get("effort", {}).get("level", "")

    def windows(self, session: str) -> tuple[RateWindow, ...]:
        return self.parsed_windows(self.status(session).get("rate_limits") or self.account_limits())

    def session_windows(self, session: str) -> tuple[RateWindow, ...]:
        return self.parsed_windows(self.status(session).get("rate_limits") or {})

    @staticmethod
    def parsed_windows(limits: dict) -> tuple[RateWindow, ...]:
        return tuple(RateWindow(key, label, limits[key].get("used_percentage", 0), limits[key].get("resets_at", 0)) for key, label in (("five_hour", "5h"), ("seven_day", "7d")) if isinstance(limits.get(key), dict))

    def account_limits(self) -> dict:
        newest = sorted(self.home.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True) if self.home.is_dir() else []
        return next((limits for path in newest if (limits := self.status(path.stem).get("rate_limits"))), {})

    def reading(self, session: str) -> AgentStatus:
        return self.status_reading(session, self.windows(session))

    def session_reading(self, session: str) -> AgentStatus:
        return self.status_reading(session, self.session_windows(session))

    def status_reading(self, session: str, windows: tuple[RateWindow, ...]) -> AgentStatus:
        return AgentStatus(self.model(session), self.effort(session), self.build(session), windows)
