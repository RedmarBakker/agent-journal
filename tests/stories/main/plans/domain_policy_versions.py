from journal.features.tasks.states.ready import Ready
from journal.features.organization.support.organization import Organization
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.domain_policy_plan import DomainPolicyPlan


@story(DomainPolicyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_closed_sprint_keeps_its_done_policy_version_when_the_domain_policy_changes(story):
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    closed = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{closed}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{closed}/start", {})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{closed}")
    development = story.app.container.get(Organization).contracts().domain("development")
    original_version = development.definition_of_done.version
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "domain"), "development")
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "criteria_version"), original_version)
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "definition_of_done", "criterion"), "The committed revision is deployed successfully to production.")
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "definition_of_done", "evidence"), "production_deployment")
    result = story.user_presses(f"/journal/sprints/{closed}/close", {})
    result.expect_viewer_passed()
    path = story.app.config.root / "r02-policy-version" / "domains" / "development" / "domain.toml"
    changed = path.read_text().replace("The committed revision is deployed successfully to production.", "The committed revision is deployed and smoke-tested in production.")
    path.write_text(changed)
    result = story.user_presses("/journal/organization/reload", {})
    result.expect_viewer_passed()
    changed_version = story.app.container.get(Organization).contracts().domain("development").definition_of_done.version
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-11-09", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    future = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{future}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{future}/start", {})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{future}")
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "criteria_version"), changed_version)
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "definition_of_done", "criterion"), "The committed revision is deployed and smoke-tested in production.")
    result = story.user_opens(f"/journal/sprints/{closed}")
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "definition_of_done", "criterion"), "The committed revision is deployed successfully to production.")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)
