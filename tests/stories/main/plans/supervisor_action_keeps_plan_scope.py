from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.in_process import posted
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.test_supervisor_actions import diagnostic_operation, maintenance_context, maintenance_request


@story(NewSession, subject=AgentRole.MAIN)
def test_a_supervisor_action_keeps_its_plan_scope_for_link_listeners(story):
    context = maintenance_context(story.app, story.monkeypatch)
    story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))
    request = maintenance_request(context, [diagnostic_operation(context)])
    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor applies a bounded diagnostic action", None, None)
    story.last_step.expect_viewer_passed()
    story.last_step.expect_viewer_shows("status", "applied")
    story.last_step.expect_viewer_part(("data", "verification"), "verified")
    story.expect_no_faults()
    fixture = context["fixture"]
    story.expect_row_in(
        fixture.owner_environment.name,
        "plans",
        fixture.plan.row_id,
        {"state": PlanState.STARTED},
    )
    story.expect_stack(story.agents.subject, Ready)
