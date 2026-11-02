from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_records import SupervisorRecords


@story(SupervisorRecords, subject=AgentRole.MAIN)
def test_a_reader_in_the_environment_reads_filtered_supervisor_counts_and_records_in_pages(story):
    plan = story.plans.first
    route = f"/journal/supervisor/records?period=last_7_days&plan_id={plan}&area=checks"
    result = story.user_opens_in(story.supervisor_environment, route)
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 102)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 51, "conflicted": 17, "proposed": 17, "rejected": 17,
    })
    result.expect_viewer_part(("current", "verified_receipts"), 30)
    result.expect_viewer_part(("previous", "runs"), 2)
    result.expect_viewer_part(("previous", "receipts"), {
        "applied": 1, "conflicted": 0, "proposed": 1, "rejected": 0,
    })
    result.expect_viewer_part(("previous", "verified_receipts"), 1)
    result.expect_viewer_count("records", 100)
    result.expect_viewer_part_is_truthy(("next_before",))

    before = story.viewer_answer["next_before"]
    result = story.user_opens_in(story.supervisor_environment, f"{route}&before={before}")
    result.expect_viewer_passed()
    result.expect_viewer_count("records", 100)
    result.expect_viewer_part_is_truthy(("next_before",))

    before = story.viewer_answer["next_before"]
    result = story.user_opens_in(story.supervisor_environment, f"{route}&before={before}")
    result.expect_viewer_passed()
    result.expect_viewer_count("records", 4)
    result.expect_viewer_part(("next_before",), None)

    result = story.user_opens_in(story.supervisor_environment, "/journal/supervisor/records?period=last_7_days")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 105)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 53, "conflicted": 17, "proposed": 17, "rejected": 17,
    })

    result = story.user_opens_in(story.supervisor_environment,
                                 f"/journal/supervisor/records?period=last_7_days&plan_id={plan}&area=plans-and-tasks")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 2)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 2, "conflicted": 0, "proposed": 0, "rejected": 0,
    })

    result = story.user_opens_in(story.supervisor_environment,
                                 f"/journal/supervisor/records?period=last_7_days&plan_id={plan}&area=secrets")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 0)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 0, "conflicted": 0, "proposed": 0, "rejected": 0,
    })

    result = story.user_opens_in(story.supervisor_environment,
                                 f"/journal/supervisor/records?period=today&plan_id={plan}&area=checks")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 0)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 0, "conflicted": 0, "proposed": 0, "rejected": 0,
    })
    result.expect_viewer_part(("previous", "runs"), 102)
    result.expect_viewer_part(("previous", "verified_receipts"), 30)

    result = story.user_opens_in(story.supervisor_environment,
                                 f"/journal/supervisor/records?period=last_30_days&plan_id={plan}&area=checks")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 104)
    result.expect_viewer_part(("current", "verified_receipts"), 31)
    result.expect_viewer_part(("previous", "runs"), 0)
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorRecords, subject=AgentRole.MAIN)
def test_a_reader_cannot_read_supervisor_records_outside_their_environment(story):
    result = story.user_opens_in(
        f"{story.supervisor_environment}-not-shared",
        "/journal/supervisor/records?period=last_7_days",
    )
    result.expect_viewer_refused("environment")
    result = story.user_opens_in(
        story.supervisor_environment,
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.foreign_plan_id}",
    )
    result.expect_viewer_refused("plan")
    result = story.user_opens_in(
        story.supervisor_environment,
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.plans.first}&area=unknown",
    )
    result.expect_viewer_refused("area")
    story.expect_stack(story.agents.subject, Ready)
