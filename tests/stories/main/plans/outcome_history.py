from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.domain_development_delivery_accepted import DomainDevelopmentDeliveryAccepted
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_blocked_task_keeps_its_wait_interval_and_execution_attempt(story):
    task = story.tasks.started
    result = story.agent_runs(story.agents.subject, f"task block {task} 'waiting for user acceptance'")
    result.expect_command_passed()
    story.time_travel(minutes=90)
    result = story.agent_runs(story.agents.subject, f"task unblock {task}")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"task start {task}")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"task complete {task} --how 'the accepted scope is complete'")
    result.expect_command_passed()
    story.expect_task_outcome_kinds(task, "task_started", "task_blocked", "task_reopened", "task_started", "task_completed")
    story.expect_task_outcome_summary(task, waiting_seconds=5400, execution_status="completed", artifact_accepted=False, right_censored=True)
    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)


@story(DomainDevelopmentDeliveryAccepted, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_deployment_wait_ends_at_accepted_evidence_and_keeps_its_commitment(story):
    task, plan = story.tasks.first, story.plans.first
    result = story.user_opens(f"/journal/plans/{plan}/outcomes")
    result.expect_viewer_passed()
    result.expect_viewer_shows("schema_version", "plan-outcome-history-v1")
    result.expect_viewer_part(("delivery", "status"), "delivered")
    result.expect_viewer_part(("delivery", "history", 0, "state"), "accepted")
    story.expect_task_outcome_kinds(task, "task_completed", "worker_work_merged", "delivery_accepted")
    story.expect_task_outcome_summary(task, delivery_wait_seconds=172800, execution_status="completed", artifact_accepted=True, right_censored=False)
    story.expect_task_outcome_fact(task, "delivery_accepted", "policy_version")
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)
