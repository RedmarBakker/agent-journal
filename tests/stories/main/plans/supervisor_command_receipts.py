from journal.support.agent_role import AgentRole
from journal.features.tasks.states.ready import Ready
from journal.features.supervisor.support.supervisor_maintenance import diagnostic_task_values
from tests.in_process import posted
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.test_supervisor_actions import diagnostic_operation, maintenance_context, maintenance_request


@story(NewSession, subject=AgentRole.MAIN)
def test_a_plan_priorities_command_receipt_uses_the_catalogue_and_repository_events(story):
    context = maintenance_context(story.app, story.monkeypatch)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    plan_id = context["grant"]["plan_id"]
    operation = {"kind": "plan_priorities", "plan_id": plan_id, "text": "Check the failure first"}
    request = maintenance_request(context, [operation])
    with context["scope"].environment(context["fixture"].owner_environment.row_id):
        before = context["maintenance"].plans.find(plan_id).priorities

    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor applies plan priorities and records its command receipt", None, None)
    receipt = story.last_step
    receipt.expect_viewer_passed()
    receipt.expect_viewer_part(("data", "command_receipts", 0, "command"), "plan priorities")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "arguments"), {"plan_id": plan_id, "text": operation["text"]})
    receipt.expect_viewer_part(("data", "command_receipts", 0, "area"), "Plans and tasks")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 1")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "status"), "applied")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "verified")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "settled_cost"), {
        "status": "settled", "usd": "0.000001", "scope": "run",
    })
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "event"), "updated")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "ref"), {"table": "plans", "id": plan_id})
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "before", "priorities"), before)
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "after", "priorities"), operation["text"])
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_task_create_command_receipt_contains_its_created_row_events(story):
    context = maintenance_context(story.app, story.monkeypatch)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    request = maintenance_request(context, [diagnostic_operation(context)])
    title, _brief = diagnostic_task_values(context["fixture"].template)

    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor creates a diagnostic task and records its command receipt", None, None)
    receipt = story.last_step
    receipt.expect_viewer_passed()
    receipt.expect_viewer_part(("data", "command_receipts", 0, "command"), "task create")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "area"), "Plans and tasks")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 1")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "status"), "applied")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "verified")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "settled_cost"), {
        "status": "settled", "usd": "0.000001", "scope": "run",
    })
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "event"), "created")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "ref", "table"), "tasks")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "before"), None)
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "after", "title"), title)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_check_edit_command_receipt_uses_the_checks_catalogue_area(story):
    context = maintenance_context(story.app, story.monkeypatch)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    check_id = context["fixture"].check.row_id
    with context["scope"].environment(context["fixture"].owner_environment.row_id):
        before = context["maintenance"].checks.find(check_id).interval
    operation = {"kind": "check_interval", "check_id": check_id, "interval_minutes": 5}
    request = maintenance_request(context, [operation])

    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor edits a check and records its command receipt", None, None)
    receipt = story.last_step
    receipt.expect_viewer_passed()
    receipt.expect_viewer_part(("data", "command_receipts", 0, "command"), "check edit")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "arguments"), {"check_id": check_id, "interval_minutes": 5})
    receipt.expect_viewer_part(("data", "command_receipts", 0, "area"), "Checks")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 1")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "status"), "applied")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "verified")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "settled_cost"), {
        "status": "settled", "usd": "0.000001", "scope": "run",
    })
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "ref"), {"table": "checks", "id": check_id})
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "before"), {"interval": before})
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed", 0, "after"), {"interval": 5.0})
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_conflicted_command_receipt_has_no_written_rows(story):
    context = maintenance_context(story.app, story.monkeypatch)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    plan_id = context["grant"]["plan_id"]
    request = maintenance_request(context, [{"kind": "plan_priorities", "plan_id": plan_id, "text": "Check the failure first"}])
    with context["scope"].environment(context["fixture"].owner_environment.row_id):
        phase = context["fixture"].phase
        context["maintenance"].plans.phases.save(phase.with_(title="Edited current phase"), context["fixture"].owner)

    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor records a conflicted plan command without writes", None, None)
    receipt = story.last_step
    receipt.expect_viewer_passed()
    receipt.expect_viewer_shows("status", "conflicted")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "command"), "plan priorities")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "area"), "Plans and tasks")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 1")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "status"), "conflicted")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "not_applied")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed"), [])
    receipt.expect_viewer_part(("data", "command_receipts", 0, "settled_cost"), {
        "status": "settled", "usd": "0.000001", "scope": "run",
    })
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_rejected_command_receipt_records_the_disabled_capability(story):
    context = maintenance_context(story.app, story.monkeypatch)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    plan_id = context["grant"]["plan_id"]
    request = maintenance_request(context, [{"kind": "plan_priorities", "plan_id": plan_id, "text": "Check the failure first"}])
    story.monkeypatch.setattr(type(context["fixture"].authority), "permits_domain_write", lambda *_: False)

    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor records a rejected plan command without writes", None, None)
    receipt = story.last_step
    receipt.expect_viewer_passed()
    receipt.expect_viewer_shows("status", "rejected")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "command"), "plan priorities")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "area"), "Plans and tasks")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 1")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "status"), "rejected")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "readback_verification"), "not_applied")
    receipt.expect_viewer_part(("data", "command_receipts", 0, "rows_changed"), [])
    receipt.expect_viewer_part(("data", "command_receipts", 0, "settled_cost"), {
        "status": "settled", "usd": "0.000001", "scope": "run",
    })
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
