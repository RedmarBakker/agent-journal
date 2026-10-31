from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_shared_sprint_forecast_keeps_an_unresolved_cross_plan_delivery_gate_bounded(story):
    source_task = story.tasks.first
    other_plan = story.user_creates_plan("dependent delivery", "use the deployed source")
    gate = story.user_presses(f"/journal/plans/{other_plan}/tasks", {
        "title": "use the deployed source", "brief": "- the source is used after deployment",
        "domain": "development", "size": 2, "delivery_gate_for": source_task,
        "reason": "this plan consumes the other plan's production deployment",
    })
    gate.expect_viewer_passed()
    gate_id = gate.viewer_answer["id"]

    sprint = story.user_presses("/journal/sprints", {
        "starts_on": "2026-10-26", "timezone": "Europe/Amsterdam",
    })
    sprint.expect_viewer_passed()
    sprint_id = sprint.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint_id}/plans", {"plan_id": other_plan}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint_id}/start", {}).expect_viewer_passed()

    forecast = story.user_opens(f"/journal/sprints/{sprint_id}/forecast")

    forecast.expect_viewer_part(("network_forecast", "status"), "unknown constraints")
    forecast.expect_viewer_part(("network_forecast", "p50"), None)
    forecast.expect_viewer_part(("network_forecast", "external_conditions"), [
        {"task_id": gate_id, "prerequisite_id": source_task, "kind": "delivery_gate",
         "external": True, "status": "unresolved"},
    ])
    story.expect_stack(story.agents.subject, Ready)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_report_forecast_reads_the_owners_shared_wip_ceilings(story):
    settings = [
        (EstimatesOptions.EXECUTION_WIP_LIMIT, 1, "execution"),
        (EstimatesOptions.WORKER_QUEUE_WIP_LIMIT, 2, "worker_queue"),
        (EstimatesOptions.PLAN_DELIVERY_WIP_LIMIT, 3, "plan_delivery"),
        (EstimatesOptions.DOMAIN_DELIVERY_WIP_LIMIT, 4, "domain_delivery"),
    ]
    for option, value, _key in settings:
        story.user_sets(option, value).expect_viewer_passed()

    sprint = story.user_presses("/journal/sprints", {
        "starts_on": "2026-10-26", "timezone": "Europe/Amsterdam",
    })
    sprint.expect_viewer_passed()
    sprint_id = sprint.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint_id}/plans", {"plan_id": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint_id}/start", {}).expect_viewer_passed()

    forecast = story.user_opens(f"/journal/sprints/{sprint_id}/forecast")

    forecast.expect_viewer_part(("network_forecast", "mode"), "report")
    for _option, value, key in settings:
        forecast.expect_viewer_part(("network_forecast", "wip_limits", key), value)
    story.expect_task(story.tasks.first, state="open")
    story.expect_stack(story.agents.subject, Ready)
