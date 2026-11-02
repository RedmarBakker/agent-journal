from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.shared_organization_domain_seat_started import SharedOrganizationDomainSeatStarted


@story(SharedOrganizationDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_shared_role_cannot_return_a_task_from_another_organizations_environment(story):
    other = "another-organization"
    story.another_environment(other)
    plan = story.user_creates_plan_in(other, "the other organization")
    created = story.user_presses_in(other, f"/journal/plans/{plan}/tasks", {"title": "private task", "domain": "alpha"})
    created.expect_viewer_passed()
    task = created.viewer_answer["id"]
    rig = story.shared_rig_name(story.plans.first)
    role = story.organization_seat_agent("role:alpha/shared", rig)
    story.agent_starts_organization_seat(role, "role:alpha/shared", rig).expect_allowed(role)

    refused = story.agent_runs_as_organization_seat(role, "role:alpha/shared", f"organization handoff {task} domain:alpha", rig)
    refused.expect_command_refused()
    refused.expect_command_text(f"task {task} is not in this organization's rig")
    story.expect_task_in(other, task, TaskState.OPEN.value)
    story.expect_stack(story.agents.main, CoordinatingPlans)
