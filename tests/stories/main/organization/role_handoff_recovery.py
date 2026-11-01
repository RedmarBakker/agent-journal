from journal.engine.states.void import Void
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_role_worker_ended import OrganizationRoleWorkerEnded
from tests.stories.fixtures.main.shared_role_queue import awaiting_state

FRESH_BRIEF = "- task 6 has its revised brief"
OLD_BRIEF = "- task 6 has its current brief"


@story(OrganizationRoleWorkerEnded, subject=AgentRole.MAIN)
def test_a_handoff_restarts_its_ended_role_worker_with_the_current_task_brief(story):
    task = story.tasks.second
    worker = story.agents.workers.first()
    story.user_rewrites_the_brief(task, FRESH_BRIEF)
    result = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    result.expect_command_passed()
    result.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_worker_role_job(worker, task, FRESH_BRIEF, OLD_BRIEF)
    story.agent_starts_role_session(worker)
    story.expect_role_job_prompt(worker, FRESH_BRIEF, OLD_BRIEF, "journal clock-in")
    clocked_in = story.agent_clocks_in(worker)
    clocked_in.expect_command_passed()
    story.expect_worker(worker, state=WorkerState.READY)
    story.expect_stack(worker, Void, WorkingTask)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan, awaiting_state(story))
