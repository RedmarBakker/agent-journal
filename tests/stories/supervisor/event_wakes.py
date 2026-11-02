from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_event_wake import SupervisorEventWake
from tests.stories.fixtures.supervisor.supervisor_event_wake_off import SupervisorEventWakeOff


def event_wake(story, event_kind):
    return story.supervisor_posts("/_supervisor/v1/admit", {
        "protocol_version": 1,
        "source": "hint",
        "observation_cursor": None,
        "wakeup_id": f"wakeup-{event_kind}",
        "kind": "checks.updated",
        "event_kind": event_kind,
        "event_id": f"event-{event_kind}",
    })


@story(SupervisorEventWake, subject=AgentRole.SUPERVISOR)
def test_each_enabled_event_kind_wakes_the_supervisor_with_its_kind(story):
    failed_check = event_wake(story, "failed_check")
    failed_check.expect_viewer_passed()
    failed_check.expect_viewer_part(("status",), "admitted")
    run = failed_check.viewer_answer["run"]
    observation = story.supervisor_posts("/_supervisor/v1/observe", {
        "protocol_version": 1,
        "run_id": run["run_id"],
        "installation_epoch": run["installation_epoch"],
        "fence": run["fence"],
        "cursor": None,
    })
    observation.expect_viewer_passed()
    observation.expect_viewer_part(("snapshot", "wake", "kind"), "event")
    observation.expect_viewer_part(("snapshot", "wake", "event_kind"), "failed_check")

    stalled_task = event_wake(story, "stalled_task")
    stalled_task.expect_viewer_passed()
    stalled_task.expect_viewer_part(("status",), "admitted")

    stale_worker = event_wake(story, "stale_worker")
    stale_worker.expect_viewer_passed()
    stale_worker.expect_viewer_part(("status",), "admitted")

    message = event_wake(story, "message_to_supervisor")
    message.expect_viewer_passed()
    message.expect_viewer_part(("status",), "admitted")

    question = event_wake(story, "question_to_supervisor")
    question.expect_viewer_passed()
    question.expect_viewer_part(("status",), "admitted")

    history = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "event"), 5)
    history.expect_viewer_part(("records", 0, "event_kind"), "question_to_supervisor")
    history.expect_viewer_part(("records", 0, "status"), "admitted")
    history.expect_viewer_part(("records", 1, "event_kind"), "message_to_supervisor")
    history.expect_viewer_part(("records", 1, "status"), "admitted")
    history.expect_viewer_part(("records", 2, "event_kind"), "stale_worker")
    history.expect_viewer_part(("records", 2, "status"), "admitted")
    history.expect_viewer_part(("records", 3, "event_kind"), "stalled_task")
    history.expect_viewer_part(("records", 3, "status"), "admitted")
    history.expect_viewer_part(("records", 4, "event_kind"), "failed_check")
    history.expect_viewer_part(("records", 4, "status"), "admitted")
    story.expect_stack(story.agents.subject)


@story(SupervisorEventWakeOff, subject=AgentRole.SUPERVISOR)
def test_an_event_with_its_grant_switch_off_does_not_wake_the_supervisor(story):
    story.user_types_in(story.fixture.supervisor_owner_environment, "Tell the supervisor the service is slow.")

    wake = event_wake(story, "message_to_supervisor")
    wake.expect_viewer_passed()
    wake.expect_viewer_part(("reason",), "event_disabled")

    history = story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )
    history.expect_viewer_passed()
    history.expect_viewer_part(("current", "wake_ups", "event"), 0)
    story.expect_stack(story.agents.subject)
