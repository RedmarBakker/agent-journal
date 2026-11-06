from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import SupervisorScheduledWake, scheduled_wake


def records(story):
    return story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )


def expect_grant_covers_plan(story):
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_scheduled_wake_with_no_change_is_skipped_as_quiet(story):
    expect_grant_covers_plan(story)
    story.time_travel(minutes=15)
    first = scheduled_wake(story)
    first.expect_viewer_passed()
    first.expect_viewer_part(("reason",), "empty")

    story.time_travel(minutes=15)
    quiet = scheduled_wake(story)
    quiet.expect_viewer_passed()
    quiet.expect_viewer_part(("reason",), "quiet")

    history = records(story)
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "runs"), 0)
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 2)
    history.expect_viewer_part(("records", 0, "reason"), "quiet")
    story.expect_stack(story.agents.subject)


@story(SupervisorScheduledWake, subject=AgentRole.SUPERVISOR)
def test_a_task_change_keeps_the_next_scheduled_wake_from_being_quiet(story):
    expect_grant_covers_plan(story)
    before = records(story)
    before.expect_viewer_passed()
    before.expect_viewer_part(("current", "wake_ups", "scheduled"), 0)

    story.time_travel(minutes=15)
    first = scheduled_wake(story)
    first.expect_viewer_passed()
    first.expect_viewer_part(("reason",), "empty")

    changed = story.user_types_in(
        story.fixture.supervisor_owner_environment,
        f"task edit {story.fixture.task_id} --title 'Inspect the service after its change'",
    )
    changed.expect_command_passed()

    story.time_travel(minutes=15)
    next_wake = scheduled_wake(story)
    next_wake.expect_viewer_passed()
    next_wake.expect_viewer_part(("reason",), "empty")

    history = records(story)
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 2)
    history.expect_viewer_part(("records", 0, "reason"), "empty")
    story.expect_stack(story.agents.subject)
