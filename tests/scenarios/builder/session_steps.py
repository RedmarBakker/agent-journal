from journal.engine.nudge import Nudge
from journal.repositories.environments import Environments
from journal.support.caller import Caller
from tests.full_project import MAIN
from tests.in_process import got, posted
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from tests.scenarios.builder.hook_verdict import HookVerdict


class SessionSteps:
    """Sessions in a story: another session starting in the same environment, of the scenario's provider or of the other, another environment of the project as its launcher makes one, and the agent's row read through the API to see which session holds it."""

    def another_environment(self, name: str) -> str:
        self.app.container.get(Environments).lookup(name)
        self.observed(f"the project has another environment, {name}", None, None)
        return name

    def task_numbers_in(self, environment: str) -> set[int]:
        return set(self.task_states_in(environment))

    def task_states_in(self, environment: str) -> dict[int, str]:
        return {row["id"]: row["state"] for row in got(self.app, "/journal/tasks", {"X-Journal-Env": environment})[1]["rows"]}

    def agent_in_starts_task(self, environment: str, session: str, title: str) -> int:
        self.session_starts_in(environment, session)
        result = self.app.console().run(["task", "create", title, "--start"], Caller.agent(environment, session, self.provider))
        assert result.code == 0, result.error
        return max(self.task_numbers_in(environment))

    def session_starts_in(self, environment: str, session: str) -> None:
        status, answer = posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}, {"X-Journal-Env": environment})
        self.observed(f"a session starts in {environment}", HookVerdict(self.provider, status, answer if isinstance(answer, dict) else {}), None)

    def expect_told_in(self, environment: str, nudge: Nudge, **values) -> None:
        said = self.log.said_in(environment)
        assert any(line.matches(nudge.key, values) for line in said), f"the agent in {environment} was not told {nudge.key} {values}: told {[(line.key, line.values) for line in said]}"

    def second_session_starts(self, session: str = "s2") -> None:
        self.session_starts_with(self.provider, session)

    def other_provider_session_starts(self, session: str = "s3") -> None:
        self.session_starts_with(next(program.name for program in (Claude, Codex) if program.name != self.provider), session)

    def session_starts_with(self, provider: str, session: str) -> None:
        status, answer = posted(self.app, f"/hooks/{provider}", {"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}, MAIN)
        self.observed(f"a {'second' if provider == self.provider else 'another provider'}'s session starts", HookVerdict(provider, status, answer if isinstance(answer, dict) else {}), None)

    def expect_agent_session(self, session: str) -> None:
        sessions = [row.get("session") for row in got(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("role") in (None, "main")]
        assert sessions == [session], f"the environment's agents hold the sessions {sessions}, not only {session}"
