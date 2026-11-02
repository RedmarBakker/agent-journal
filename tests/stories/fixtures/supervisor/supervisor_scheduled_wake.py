from journal.engine.clock import Clock
from journal.repositories.environments import Environments
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SupervisorAuthority
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.test_supervisor_authority import enrollment, seeded


class SupervisorScheduledWake(SupervisorGrantFixture):
    """An active supervisor grant has a pinned scheduled wake interval."""

    parent = NewSession
    valid_for_minutes = 180
    event_wakeups = ("failed_check",)
    daily_cost_limit_microusd = 10_000
    max_input_tokens_per_turn = 1_000
    max_output_tokens_per_turn = 1_000
    story_start_at = None

    def steps(self, story) -> None:
        self.restore_on(story)
        if self.story_start_at is not None:
            story.app.container.get(TimeSource).pin(self.story_start_at)
            story.app.container.get(Clock).held_at = self.story_start_at
        fixture = seeded(story.app, owner_id=1)
        authority = story.app.container.get(SupervisorAuthority)
        request = enrollment(fixture, "shadow")
        request["event_wakeups"] = list(self.event_wakeups)
        request["limits"]["max_input_tokens_per_turn"] = self.max_input_tokens_per_turn
        request["limits"]["max_output_tokens_per_turn"] = self.max_output_tokens_per_turn
        request["limits"]["max_cost_microusd_per_day"] = self.daily_cost_limit_microusd
        request["valid_until_ms"] = int((story.app.container.get(TimeSource).seconds() + self.valid_for_minutes * 60) * 1000)
        grant, token = authority.enroll(fixture["owner"], request)
        fixture["credentials"].append(authority._credential_name(grant["grant_id"], grant["grant_version"]))
        self.supervisor_credential = token
        self.supervisor_owner_environment = story.app.container.get(Environments).find(
            fixture["owner_environment"].row_id,
        ).name
        self.task_id = fixture["task"].row_id
        story.plans.first = grant["plan_id"]
        story.grants.first = grant["grant_id"]
        story.closers.append(lambda: authority.secrets_store.drop(fixture["credentials"]))
        opened = story.user_opens_in(self.supervisor_owner_environment, "/journal/plans")
        opened.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.subject)


class SupervisorScheduledWakeExpiresSoon(SupervisorScheduledWake):
    """An active supervisor grant expires before its next scheduled wake."""

    valid_for_minutes = 10
