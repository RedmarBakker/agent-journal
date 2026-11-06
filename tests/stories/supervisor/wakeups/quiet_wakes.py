from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_quiet_wakes import SupervisorQuietWakes
from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import scheduled_wake


def records(story):
    return story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.plans.first}",
    )


def expect_grant_covers_plan(story):
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)


@story(SupervisorQuietWakes, subject=AgentRole.SUPERVISOR)
def test_a_new_grant_records_empty_then_quiets_an_unchanged_wake(story):
    expect_grant_covers_plan(story)
    first = scheduled_wake(story)
    first.expect_viewer_passed()
    first.expect_viewer_part(("reason",), "empty")

    early = scheduled_wake(story)
    early.expect_viewer_passed()
    early.expect_viewer_part(("reason",), "scheduled_interval_not_elapsed")

    story.time_travel(minutes=15)
    due = scheduled_wake(story)
    due.expect_viewer_passed()
    due.expect_viewer_part(("reason",), "quiet")

    history = records(story)
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "runs"), 0)
    history.expect_viewer_part(("current", "wake_ups", "scheduled"), 2)
    history.expect_viewer_part(("records", 0, "reason"), "quiet")
    history.expect_viewer_part(("records", 1, "reason"), "empty")
    story.expect_stack(story.agents.subject)


@story(SupervisorQuietWakes, subject=AgentRole.SUPERVISOR)
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
