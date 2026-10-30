from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.domain_development_delivered import DomainDevelopmentDelivered


@story(DomainDevelopmentDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_merged_development_plan_remains_awaiting_deployment_in_all_forecast_views(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.first}")
    merged = story.agent_runs(story.agents.subject, f"worker merge {worker}")
    merged.expect_command_passed()

    sprint = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    sprint.expect_viewer_passed()
    sprint_id = sprint.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint_id}/plans", {"plan_id": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint_id}/start", {}).expect_viewer_passed()

    plan = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    plan.expect_viewer_shows("status", "not enough history")
    plan.expect_viewer_shows("p50", None)
    plan.expect_viewer_shows("probability_this_sprint", None)
    plan.expect_viewer_shows("delivery_status", "awaiting deployment")
    plan.expect_viewer_shows("delivery_complete", False)
    plan.expect_viewer_shows("delivered_scope", [])
    plan.expect_viewer_shows("awaiting_deploy_count", 1)
    plan.expect_viewer_part(("domain_criteria", 0, "criterion"), "A successful production deployment of the committed revision.")

    organization = story.user_opens("/journal/organization")
    organization.expect_viewer_part(("sprint_forecasts", 0, "sprint", "id"), sprint_id)
    organization.expect_viewer_part(("sprint_forecasts", 0, "forecast", "status"), plan.viewer_answer["status"])
    organization.expect_viewer_part(("sprint_forecasts", 0, "forecast", "plan_forecasts", 0, "delivery_status"), "awaiting deployment")
    organization.expect_viewer_part(("sprint_forecasts", 0, "forecast", "plan_forecasts", 0, "p50"), None)
    organization.expect_viewer_part(("sprint_forecasts", 0, "forecast", "plan_forecasts", 0, "probability_this_sprint"), plan.viewer_answer["probability_this_sprint"])
    organization.expect_viewer_part(("plans", 0, "id"), story.plans.first)
    organization.expect_viewer_part(("plans", 0, "story_points", "unknown_tasks"), 1)
    story.expect_stack(story.agents.subject, Ready)
