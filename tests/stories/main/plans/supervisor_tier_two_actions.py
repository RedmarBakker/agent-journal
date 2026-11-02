from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.in_process import posted
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.test_supervisor_actions import maintenance_context, maintenance_request


def plan_tell_action(story, mode: str):
    decision = "may_act" if mode == "bounded_write" else "propose_only"
    context = maintenance_context(
        story.app, story.monkeypatch, mode, capability_decisions={"plan tell": decision}, owner_id=1,
    )
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    plan_id = context["grant"]["plan_id"]
    operation = {"kind": "plan_tell", "plan_id": plan_id, "text": "Review the failed check first"}
    request = maintenance_request(context, [operation])
    return context, plan_id, operation, request


@story(NewSession, subject=AgentRole.MAIN)
def test_a_tier_two_act_runs_and_records_its_receipt(story):
    context, _plan_id, operation, request = plan_tell_action(story, "bounded_write")
    story.viewer_status, story.viewer_answer = posted(
        story.app, "/_supervisor/v1/apply", request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor tells the plan agent through a tier 2 command", None, None)
    result = story.last_step
    result.expect_viewer_passed()
    result.expect_viewer_part(("data", "status"), "applied")
    result.expect_viewer_part(("data", "command_receipts", 0, "command"), "plan tell")
    result.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 2")
    result.expect_viewer_part(("data", "command_receipts", 0, "status"), "applied")
    result.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "verified")
    result.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "event"), "created")
    result.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "ref", "table"), "messages")
    result.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "after", "text"), operation["text"])
    message_id = result.viewer_answer["data"]["affected_refs"][0]["id"]
    story.expect_row_in(context["fixture"].driver_environment.name, "messages", message_id, {"text": operation["text"]})
    history = story.user_opens_in(
        context["fixture"].owner_environment.name, "/journal/supervisor/records?period=today",
    )
    history.expect_viewer_passed()
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_tier_two_propose_stores_the_command_without_running_it(story):
    context, _plan_id, operation, request = plan_tell_action(story, "shadow")
    story.viewer_status, story.viewer_answer = posted(
        story.app, "/_supervisor/v1/apply", request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor proposes telling the plan agent with a tier 2 command", None, None)
    result = story.last_step
    result.expect_viewer_passed()
    result.expect_viewer_part(("data", "status"), "proposed")
    result.expect_viewer_part(("data", "proposed_operations", 0), operation)
    result.expect_viewer_part(("data", "affected_refs"), [])
    result.expect_viewer_part(("data", "command_receipts"), [])
    receipt_id = result.viewer_answer["receipt_id"]
    control = story.user_opens_in(context["fixture"].owner_environment.name, "/journal/supervisor/control")
    control.expect_viewer_passed()
    control.expect_viewer_part(("proposals", 0, "receipt_id"), receipt_id)
    control.expect_viewer_part(("proposals", 0, "actions", 0, "receipt_status"), "proposed")
    control.expect_viewer_part(("proposals", 0, "actions", 0, "tier"), 2)
    story.expect_row_count_in(context["fixture"].driver_environment.name, "messages", 0)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
