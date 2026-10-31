from journal.features.tasks.states.ready import Ready
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_forecast_shows_declared_dependencies_and_independent_work_as_a_structural_graph(story):
    prerequisite = story.tasks.first
    dependent = story.agent_runs(
        story.agents.subject,
        f"plan add {story.plans.first} 'deploy' --brief 'the artifact is deployed' --domain development "
        f"--size 5 --phase 1 --after {prerequisite} --reason 'deployment uses the built artifact'",
    )
    dependent.expect_command_passed()
    dependent_id = story.created_number("task")
    independent = story.agent_runs(
        story.agents.subject,
        f"plan add {story.plans.first} 'notify' --brief 'the release notice is published' "
        "--domain development --size 2 --phase 1",
    )
    independent.expect_command_passed()
    independent_id = story.created_number("task")

    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_part(("critical_path", "status"), "structural")
    forecast.expect_viewer_part(("critical_path", "basis"), "structural dependency graph")
    forecast.expect_viewer_part(("critical_path", "p50_finish"), None)
    forecast.expect_viewer_part(("critical_path", "critical_task_ids"), [])
    forecast.expect_viewer_part(("critical_path", "edges"), [
        {"task_id": dependent_id, "prerequisite_id": prerequisite, "kind": "prerequisite", "external": False},
    ])
    forecast.expect_viewer_part(("critical_path", "external_conditions"), [])
    forecast.expect_viewer_part(("critical_path", "independent_groups"), [[independent_id]])
    forecast.expect_viewer_part(("critical_path", "tasks", 0, "earliest_start"), None)
    forecast.expect_viewer_part(("critical_path", "tasks", 0, "slack_days"), None)
    story.expect_stack(story.agents.subject, Ready)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_forecast_names_an_unresolved_cross_plan_delivery_gate(story):
    source_plan = story.user_creates_plan("source delivery", "the source artifact is deployed")
    source_task = story.user_adds_plan_task(source_plan, "source artifact", "development")
    gate = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {
        "title": "use the deployed source", "brief": "- the source is used after deployment",
        "domain": "development", "size": 2, "delivery_gate_for": source_task,
        "reason": "this plan consumes the other plan's production deployment",
    })
    gate.expect_viewer_passed()
    gate_id = gate.viewer_answer["id"]

    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_part(("critical_path", "status"), "structural")
    forecast.expect_viewer_part(("critical_path", "edges"), [
        {"task_id": gate_id, "prerequisite_id": source_task, "kind": "delivery_gate", "external": True},
    ])
    forecast.expect_viewer_part(("critical_path", "external_conditions"), [
        {"task_id": gate_id, "prerequisite_id": source_task, "kind": "delivery_gate", "external": True, "status": "unresolved"},
    ])
    forecast.expect_viewer_part(("critical_path", "p50_finish"), None)
    story.expect_stack(story.agents.subject, Ready)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_builder_is_told_about_a_truly_independent_task(story):
    prerequisite = story.tasks.first
    dependent = story.agent_runs(
        story.agents.subject,
        f"plan add {story.plans.first} 'deploy' --brief 'the artifact is deployed' --domain development "
        f"--size 5 --phase 1 --after {prerequisite} --reason 'deployment uses the built artifact'",
    )
    dependent.expect_command_passed()
    dependent_id = story.created_number("task")
    independent = story.agent_runs(
        story.agents.subject,
        f"plan add {story.plans.first} 'notify' --brief 'the release notice is published' "
        "--domain development --size 2 --phase 1",
    )
    independent.expect_command_passed()
    independent_id = story.created_number("task")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}").expect_command_passed()
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}").expect_command_passed()

    result = story.agent_stops(story.agents.subject)

    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.CRITICAL_PATH, f"task #{independent_id}")
    story.expect_task(dependent_id, state=TaskState.OPEN, size=5)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
