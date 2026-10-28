from tests.full_project import MAIN
from tests.in_process import got, posted
from tests.scenarios.builder.hook_verdict import HookVerdict


class SessionSteps:
    """Sessions in a story: another session of the scenario's provider starting in the same environment, and the agent's row read through the API to see which session holds it."""

    def second_session_starts(self, session: str = "s2") -> None:
        status, answer = posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}, MAIN)
        self.observed("a second session starts", HookVerdict(self.provider, status, answer if isinstance(answer, dict) else {}), None)

    def expect_agent_session(self, session: str) -> None:
        sessions = [row.get("session") for row in got(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("role") in (None, "main")]
        assert sessions == [session], f"the environment's agents hold the sessions {sessions}, not only {session}"
