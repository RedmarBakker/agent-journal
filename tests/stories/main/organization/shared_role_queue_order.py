from journal.features.workers.organization_options import OrganizationOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.shared_role_queue import SharedRoleQueue, awaiting_state


@story(SharedRoleQueue, subject=AgentRole.MAIN)
@setting(OrganizationOptions.SHARED_ROLE_QUEUE_ORDER, "arrival")
def test_a_shared_role_keeps_queue_arrival_order_when_the_trial_setting_is_selected(story):
    worker = story.agents.workers.first()
    result = story.agent_runs(
        story.agents.main,
        f"worker queue {worker} {story.tasks.first_queued} {story.tasks.second_queued} {story.tasks.other_plan}",
    )
    result.expect_command_passed()
    view = story.user_opens(f"/journal/workers?ids={worker}")
    view.expect_viewer_part(("rows", 0, "queue"), [
        {"id": story.tasks.first_queued, "title": "First queued task"},
        {"id": story.tasks.second_queued, "title": "Second queued task"},
        {"id": story.tasks.other_plan, "title": "Other plan task"},
    ])
    story.expect_task(story.tasks.active, state=TaskState.STARTED)
    story.expect_plan(story.plans.first, title="Alpha delivery", state=PlanState.APPROVED)
    story.expect_plan(story.plans.second, title="Beta delivery", state=PlanState.APPROVED)
    story.expect_stack(story.agents.main, CoordinatingPlans, awaiting_state(story))
