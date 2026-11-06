from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import (
    SupervisorScheduledWake,
    SupervisorScheduledWakeExpiresSoon,
    scheduled_wake,
)


def change_interval(story, version: int, minutes: int):
    return story.user_presses("/_supervisor/v2/grant/interval", {
        "protocol_version": 2,
        "grant_id": story.grants.first,
        "expected_grant_version": version,
        "wake_interval_minutes": minutes,
    })


def expect_grant_covers_plan(story):
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_changed_thirty_minute_interval_controls_the_next_scheduled_wake(story):
    expect_grant_covers_plan(story)
    first = scheduled_wake(story)
    first.expect_viewer_passed()
    first.expect_viewer_part(("reason",), "quiet")

    control = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        "/journal/supervisor/control",
    )
    control.expect_viewer_passed()
    control.expect_viewer_part(("grant", "wake_interval_minutes"), 15)

    changed = change_interval(story, 1, 30)
    changed.expect_viewer_passed()
    changed.expect_viewer_part(("grant_version",), 2)
    changed.expect_viewer_part(("wake_interval_minutes",), 30)

    story.time_travel(minutes=29)
    early = scheduled_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=1)
    due = scheduled_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "quiet")
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_changed_sixty_minute_interval_controls_the_next_scheduled_wake(story):
    expect_grant_covers_plan(story)
    first = scheduled_wake(story)
    first.expect_viewer_passed()
    first.expect_viewer_part(("reason",), "quiet")

    changed = change_interval(story, 1, 60)
    changed.expect_viewer_passed()
    changed.expect_viewer_part(("grant_version",), 2)
    changed.expect_viewer_part(("wake_interval_minutes",), 60)

    story.time_travel(minutes=59)
    early = scheduled_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=1)
    due = scheduled_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "quiet")
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_paused_supervisor_has_no_scheduled_wake(story):
    expect_grant_covers_plan(story)
    paused = story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": 1,
        "change": {"kind": "off"},
    })
    paused.expect_viewer_passed()

    story.time_travel(minutes=15)
    wake = scheduled_wake(story)
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
    expect_grant_covers_plan(story)
    story.time_travel(minutes=11)
    wake = scheduled_wake(story)
    wake.expect_viewer_refused("the supervisor grant is no longer current")
    history = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 0)
    story.expect_stack(story.agents.subject)
