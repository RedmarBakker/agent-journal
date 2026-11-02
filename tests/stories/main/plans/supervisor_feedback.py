from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_owner_action import SupervisorOwnerAction


def feedback_route(plan_id: int) -> str:
    return f"/journal/plans/{plan_id}/supervisor/feedback"


def feedback_item_route(plan_id: int, feedback_id: int) -> str:
    return f"{feedback_route(plan_id)}/{feedback_id}"


def action_feedback(fixture) -> dict:
    return {
        "decision_kind": "action",
        "decision_id": fixture.receipt_id,
        "verdict": "Useful",
        "comment": "The plan priorities change was helpful.",
        "correction": "Should have done nothing",
        "scenario": {
            "plan": fixture.plan_id,
            "area": "Plans and tasks",
            "verb": "plan priorities",
            "wake_event": "failed_check",
        },
    }


@story(SupervisorOwnerAction, subject=AgentRole.MAIN)
def test_the_owner_gives_feedback_on_a_supervisor_action(story):
    fixture = story.fixture
    created = story.user_presses_in(
        fixture.environment_name, feedback_route(fixture.plan_id), action_feedback(fixture),
    )
    created.expect_viewer_passed()
    created.expect_viewer_part(("verdict",), "Useful")
    created.expect_viewer_part(("creator",), fixture.owner_actor.stamp)

    saved = story.user_opens_in(fixture.environment_name, feedback_route(fixture.plan_id))
    saved.expect_viewer_passed()
    saved.expect_viewer_part(("feedback", 0, "decision", "kind"), "action")
    saved.expect_viewer_part(("feedback", 0, "decision", "id"), fixture.receipt_id)
    saved.expect_viewer_part(("feedback", 0, "correction"), "Should have done nothing")
    saved.expect_viewer_part(("feedback", 0, "scenario", "plan"), fixture.plan_id)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorOwnerAction, subject=AgentRole.MAIN)
def test_the_owner_edits_feedback_and_keeps_its_action_link(story):
    fixture = story.fixture
    created = story.user_presses_in(
        fixture.environment_name, feedback_route(fixture.plan_id), action_feedback(fixture),
    )
    created.expect_viewer_passed()
    feedback_id = created.viewer_answer["id"]

    edited = story.user_presses_in(
        fixture.environment_name, feedback_item_route(fixture.plan_id, feedback_id), {
            "verdict": "Not useful",
            "comment": "The owner priorities were already correct.",
            "correction": "Should have handed it to me",
            "scenario": {
                "plan": fixture.plan_id,
                "area": "Plans and tasks",
                "verb": "plan priorities",
                "wake_event": "failed_check",
            },
        },
    )
    edited.expect_viewer_passed()
    edited.expect_viewer_part(("id",), feedback_id)
    edited.expect_viewer_part(("updater",), fixture.owner_actor.stamp)

    saved = story.user_opens_in(fixture.environment_name, feedback_route(fixture.plan_id))
    saved.expect_viewer_passed()
    saved.expect_viewer_count("feedback", 1)
    saved.expect_viewer_part(("feedback", 0, "verdict"), "Not useful")
    saved.expect_viewer_part(("feedback", 0, "correction"), "Should have handed it to me")
    saved.expect_viewer_part(("feedback", 0, "decision", "id"), fixture.receipt_id)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorOwnerAction, subject=AgentRole.MAIN)
def test_feedback_with_a_comment_over_1000_characters_is_refused(story):
    fixture = story.fixture
    feedback = action_feedback(fixture)
    feedback["comment"] = "x" * 1001
    refused = story.user_presses_in(
        fixture.environment_name, feedback_route(fixture.plan_id), feedback,
    )
    refused.expect_viewer_refused("1,000")
    wakeups = story.user_opens_in(
        fixture.environment_name, f"/journal/plans/{fixture.plan_id}/supervisor/wakeups",
    )
    wakeups.expect_viewer_passed()
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
