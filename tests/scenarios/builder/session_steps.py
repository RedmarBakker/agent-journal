from journal.repositories.environments import Environments
from tests.full_project import MAIN
from tests.in_process import got, posted
from tests.replay import PROVIDERS
from tests.scenarios.builder.hook_verdict import HookVerdict


class SessionSteps:
    """Sessions in a story: another session starting in the same environment, of the scenario's provider or of the other, another environment of the project as its launcher makes one, and the agent's row read through the API to see which session holds it."""

    def another_environment(self, name: str) -> str:
        self.app.container.get(Environments).lookup(name)
        self.observed(f"the project has another environment, {name}", None, None)
        return name

    def task_numbers_in(self, environment: str) -> set[int]:
        return {row["id"] for row in got(self.app, "/journal/tasks", {"X-Journal-Env": environment})[1]["rows"]}

    def second_session_starts(self, session: str = "s2") -> None:
        self.session_starts_with(self.provider, session)

    def other_provider_session_starts(self, session: str = "s3") -> None:
        self.session_starts_with(next(provider for provider in PROVIDERS if provider != self.provider), session)

    def session_starts_with(self, provider: str, session: str) -> None:
        status, answer = posted(self.app, f"/hooks/{provider}", {"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}, MAIN)
        self.observed(f"a {'second' if provider == self.provider else 'another provider'}'s session starts", HookVerdict(provider, status, answer if isinstance(answer, dict) else {}), None)

    def expect_agent_session(self, session: str) -> None:
        sessions = [row.get("session") for row in got(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("role") in (None, "main")]
        assert sessions == [session], f"the environment's agents hold the sessions {sessions}, not only {session}"
