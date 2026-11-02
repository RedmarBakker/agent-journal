from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import (
    SupervisorScheduledWake,
    SupervisorScheduledWakeExpiresSoon,
)


def timer_wake(story):
    return story.supervisor_posts("/_supervisor/v1/admit", {
        "protocol_version": 1, "source": "timer", "observation_cursor": None,
    })


def change_interval(story, version: int, minutes: int):
    return story.user_presses("/_supervisor/v2/grant/interval", {
        "protocol_version": 2,
        "grant_id": story.grants.first,
        "expected_grant_version": version,
        "wake_interval_minutes": minutes,
    })


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_scheduled_wake_waits_for_the_grant_fifteen_minute_interval(story):
    story.time_travel(minutes=14)
    early = timer_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=1)
    due = timer_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "empty")

    repeated = timer_wake(story)
    repeated.expect_viewer_passed()
    repeated.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    history = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 1)
    history.expect_viewer_part(("records", 0, "kind"), "wake")
    history.expect_viewer_part(("records", 0, "interval_minutes"), 15)
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_changed_thirty_minute_interval_controls_the_next_scheduled_wake(story):
    changed = change_interval(story, 1, 30)
    changed.expect_viewer_passed()
    changed.expect_viewer_part(("grant_version",), 2)
    changed.expect_viewer_part(("wake_interval_minutes",), 30)

    story.time_travel(minutes=29)
    early = timer_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=1)
    due = timer_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "empty")
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_changed_sixty_minute_interval_controls_the_next_scheduled_wake(story):
    changed = change_interval(story, 1, 60)
    changed.expect_viewer_passed()
    changed.expect_viewer_part(("grant_version",), 2)
    changed.expect_viewer_part(("wake_interval_minutes",), 60)

    story.time_travel(minutes=59)
    early = timer_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=1)
    due = timer_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "empty")
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_changed_wake_interval_takes_effect_after_the_current_wake(story):
    story.time_travel(minutes=15)
    due = timer_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "empty")

    changed = change_interval(story, 1, 30)
    changed.expect_viewer_passed()
    changed.expect_viewer_part(("grant_version",), 2)
    changed.expect_viewer_part(("wake_interval_minutes",), 30)

    story.time_travel(minutes=29)
    early = timer_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=1)
    next_wake = timer_wake(story)
    next_wake.expect_viewer_passed()
    next_wake.expect_viewer_part(("reason",), "empty")
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_paused_supervisor_has_no_scheduled_wake(story):
    paused = story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": 1,
        "change": {"kind": "off"},
    })
    paused.expect_viewer_passed()

    story.time_travel(minutes=15)
    wake = timer_wake(story)
    wake.expect_viewer_refused("the supervisor grant is paused")
    history = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 0)
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWakeExpiresSoon, subject=AgentRole.SUPERVISOR)
def test_an_expired_grant_has_no_scheduled_wake(story):
    story.time_travel(minutes=11)
    wake = timer_wake(story)
    wake.expect_viewer_refused("the supervisor grant is no longer current")
    history = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 0)
    story.expect_stack(story.agents.subject)
