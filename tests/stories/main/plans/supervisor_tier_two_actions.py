from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.test_supervisor_actions import maintenance_context, maintenance_request


def plan_tell(plan_id):
    return {"kind": "plan_tell", "plan_id": plan_id, "text": "Review the failed health check."}


@story(NewSession, subject=AgentRole.MAIN)
def test_a_tier_two_plan_tell_on_act_runs_and_records_its_receipt(story):
    context = maintenance_context(story.app, story.monkeypatch, command_modes={"plan tell": "act"}, owner_id=1)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    story.supervisor_credential = context["token"]
    plan_id = context["grant"]["plan_id"]

    receipt = story.supervisor_posts(
        "/_supervisor/v1/apply", maintenance_request(context, [plan_tell(plan_id)]),
    )
    receipt.expect_viewer_passed()
    receipt.expect_viewer_part(("data", "command_receipts", 0, "command"), "plan tell")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 2")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "status"), "applied")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "verified")
    message_id = story.viewer_answer["data"]["command_receipts"][0]["rows_changed"][0]["ref"]["id"]
    story.expect_row_in(context["fixture"].driver_environment.name, "messages", message_id, {
        "text": "Review the failed health check.",
    })
    history = story.user_opens_in(
        context["fixture"].owner_environment.name, "/journal/supervisor/records?period=today",
    )
    history.expect_viewer_passed()
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_tier_two_plan_tell_on_propose_is_stored_as_a_proposal(story):
    context = maintenance_context(story.app, story.monkeypatch, command_modes={"plan tell": "propose"}, owner_id=1)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    story.supervisor_credential = context["token"]
    plan_id = context["grant"]["plan_id"]

    proposal = story.supervisor_posts(
        "/_supervisor/v1/apply", maintenance_request(context, [plan_tell(plan_id)]),
    )
    proposal.expect_viewer_passed()
    proposal.expect_viewer_part(("data", "status"), "proposed")
    proposal.expect_viewer_part(("data", "proposed_operations", 0, "kind"), "plan_tell")
    receipt_id = story.viewer_answer["receipt_id"]

    control = story.user_opens_in(context["fixture"].owner_environment.name, "/journal/supervisor/control")
    control.expect_viewer_passed()
    control.expect_viewer_part(("proposals", 0, "receipt_id"), receipt_id)
    control.expect_viewer_part(("proposals", 0, "actions", 0, "receipt_status"), "proposed")
    control.expect_viewer_part(("proposals", 0, "actions", 0, "tier"), 2)
    story.expect_row_count_in(context["fixture"].driver_environment.name, "messages", 0)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
