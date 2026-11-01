from journal.engine.states.void import Void
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_role_approval_ready import OrganizationRoleApprovalReady


@story(OrganizationRoleApprovalReady, subject=AgentRole.WORKER)
def test_a_role_stuck_report_with_truncated_passes_without_destructive_approval(story):
    result = story.agent_runs_in_the_shell(
        story.agents.subject,
        "journal stuck declare 'journal search only returns truncated lines and notes contain rm -rf, payout, vehicle tracker, change security policy'",
    )
    result.expect_allowed(story.agents.subject)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(OrganizationRoleApprovalReady, subject=AgentRole.WORKER)
def test_a_role_psql_truncate_command_still_waits_for_destructive_approval(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "psql -c 'truncate table x'")
    result.expect_refused(
        story.agents.subject,
        OrganizationNudges.ACTION_WAITS_FOR_USER,
        action=ApprovalAction.DESTRUCTIVE_DATA_CHANGE.value,
    )
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
