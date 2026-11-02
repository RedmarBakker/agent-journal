from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.supervisor_grant_paused import SupervisorGrantPaused
from tests.stories.fixtures.main.supervisor_records import SupervisorRecords


def environment(story):
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    return story.app.container.get(Environments).find(plan.environment_id).name


@story(SupervisorRecords, subject=AgentRole.MAIN)
def test_a_reader_in_the_environment_reads_filtered_supervisor_counts_and_records_in_pages(story):
    plan = story.plans.first
    current = environment(story)
    route = f"/journal/supervisor/records?period=last_7_days&plan_id={plan}&area=checks"
    result = story.user_opens_in(current, route)
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "on")
    result.expect_viewer_part_is_truthy(("areas",))
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
    result = story.user_opens_in(current, f"{route}&before={before}")
    result.expect_viewer_passed()
    result.expect_viewer_count("records", 100)
    result.expect_viewer_part_is_truthy(("next_before",))

    before = story.viewer_answer["next_before"]
    result = story.user_opens_in(current, f"{route}&before={before}")
    result.expect_viewer_passed()
    result.expect_viewer_count("records", 4)
    result.expect_viewer_part(("next_before",), None)

    result = story.user_opens_in(current, "/journal/supervisor/records?period=last_7_days")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 105)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 53, "conflicted": 17, "proposed": 17, "rejected": 17,
    })

    result = story.user_opens_in(current,
                                 f"/journal/supervisor/records?period=last_7_days&plan_id={plan}&area=plans-and-tasks")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 2)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 2, "conflicted": 0, "proposed": 0, "rejected": 0,
    })

    result = story.user_opens_in(current,
                                 f"/journal/supervisor/records?period=last_7_days&plan_id={plan}&area=secrets")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 0)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 0, "conflicted": 0, "proposed": 0, "rejected": 0,
    })

    result = story.user_opens_in(current,
                                 f"/journal/supervisor/records?period=today&plan_id={plan}&area=checks")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 0)
    result.expect_viewer_part(("current", "receipts"), {
        "applied": 0, "conflicted": 0, "proposed": 0, "rejected": 0,
    })
    result.expect_viewer_part(("previous", "runs"), 102)
    result.expect_viewer_part(("previous", "verified_receipts"), 30)

    result = story.user_opens_in(current,
                                 f"/journal/supervisor/records?period=last_30_days&plan_id={plan}&area=checks")
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "runs"), 104)
    result.expect_viewer_part(("current", "verified_receipts"), 31)
    result.expect_viewer_part(("previous", "runs"), 0)
    result = story.user_opens_in(
        current,
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.plans.foreign}",
    )
    result.expect_viewer_refused("plan")
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_an_environment_without_a_supervisor_grant_is_never_set_up(story):
    result = story.user_opens_in("main", "/journal/supervisor/records?period=last_30_days")
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "never_set_up")
    result.expect_viewer_part(("current", "runs"), 0)
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorGrantPaused, subject=AgentRole.MAIN)
def test_an_owner_can_read_past_records_while_the_supervisor_is_off(story):
    result = story.user_opens_in(environment(story), "/journal/supervisor/records?period=last_30_days")
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "off")
    result.expect_viewer_part(("current", "runs"), 0)
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorRecords, subject=AgentRole.MAIN)
def test_a_reader_cannot_read_supervisor_records_outside_their_environment(story):
    result = story.user_opens_in(
        f"{environment(story)}-not-shared",
        "/journal/supervisor/records?period=last_7_days",
    )
    result.expect_viewer_refused("environment")
    result = story.user_opens_in(
        environment(story),
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.plans.foreign}",
    )
    result.expect_viewer_refused("plan")
    result = story.user_opens_in(
        environment(story),
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.plans.first}&area=unknown",
    )
    result.expect_viewer_refused("area")
    story.expect_stack(story.agents.subject, Ready)
