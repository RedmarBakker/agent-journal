from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_owner_action import SupervisorOwnerAction
from tests.stories.fixtures.main.supervisor_owner_tier_two_action import SupervisorOwnerTierTwoAction


def owner_undo_route(fixture):
    return f"/journal/plans/{fixture.plan_id}/supervisor/receipts/{fixture.receipt_id}/undo"


@story(SupervisorOwnerAction, subject=AgentRole.MAIN)
def test_the_owner_undoes_a_tier_one_receipt_and_counts_undone_by_you(story):
    fixture = story.fixture
    undone = story.user_presses_in(fixture.environment_name, owner_undo_route(fixture), {})
    undone.expect_viewer_passed()
    undone.expect_viewer_part(("report", "owner_undo", "status"), "undone")
    undone.expect_viewer_part(("report", "owner_undo", "actor"), fixture.owner_actor.stamp)
    story.expect_row_in(fixture.environment_name, "plans", fixture.plan_id, {
        "priorities": fixture.before_priorities,
    })
    counts = story.user_opens_in(
        fixture.environment_name,
        f"/journal/plans/{fixture.plan_id}/supervisor/undos",
    )
    counts.expect_viewer_passed()
    counts.expect_viewer_part(("counts", "Undone by you"), 1)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorOwnerAction, subject=AgentRole.MAIN)
def test_the_owner_cannot_undo_a_receipt_after_the_plan_changed(story):
    fixture = story.fixture
    changed = story.user_presses_in(
        fixture.environment_name, f"/journal/plans/{fixture.plan_id}", {"priorities": "Owner priority"},
    )
    changed.expect_viewer_passed()

    refused = story.user_presses_in(fixture.environment_name, owner_undo_route(fixture), {})
    refused.expect_viewer_refused("rows changed since")
    story.expect_row_in(fixture.environment_name, "plans", fixture.plan_id, {
        "priorities": "Owner priority",
    })
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorOwnerTierTwoAction, subject=AgentRole.MAIN)
def test_the_owner_cannot_undo_a_tier_two_receipt(story):
    fixture = story.fixture
    wakeups = story.user_opens_in(
        fixture.environment_name,
        f"/journal/plans/{fixture.plan_id}/supervisor/wakeups",
    )
    wakeups.expect_viewer_passed()

    refused = story.user_presses_in(fixture.environment_name, owner_undo_route(fixture), {})
    refused.expect_viewer_refused("tier 1")
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
