from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.domain_development_delivered import DomainDevelopmentDelivered
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_paused_task_keeps_its_wait_interval_and_execution_attempt(story):
    task = story.tasks.started
    result = story.agent_runs(story.agents.subject, f"task pause {task} 'waiting for user acceptance'")
    result.expect_command_passed()
    story.time_travel(minutes=90)
    result = story.agent_runs(story.agents.subject, f"task resume {task}")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"task complete {task} --how 'the accepted scope is complete'")
    result.expect_command_passed()
    story.expect_task_outcome_kinds(task, "task_started", "task_paused", "task_resumed", "task_completed")
    story.expect_task_outcome_summary(task, waiting_seconds=5400, execution_status="completed", artifact_accepted=False, right_censored=False)
    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)


@story(DomainDevelopmentDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_deployment_wait_ends_at_accepted_evidence_and_keeps_its_commitment(story):
    worker = story.agents.workers.first()
    result = story.agent_runs(story.agents.subject, f"worker check {worker} 1")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"worker merge {worker}")
    result.expect_command_passed()
    story.time_travel(days=2)
    task, plan = story.tasks.first, story.plans.first
    evidence = {"action": "accept", "evidence": {"kind": "production_deployment", "source": "deployment pipeline", "reference": "release-52",
                "artifact": "sha256:revision-52", "environment": "production", "result": "succeeded", "task_ids": [task],
                "occurred_at": "2026-10-30T10:00:00+00:00"}}
    result = story.user_presses(f"/journal/plans/{plan}/delivery", evidence)
    result.expect_viewer_passed()
    story.expect_task_outcome_kinds(task, "task_completed", "worker_work_merged", "delivery_accepted")
    story.expect_task_outcome_summary(task, delivery_wait_seconds=172800, execution_status="completed", artifact_accepted=True, right_censored=False)
    story.expect_task_outcome_fact(task, "delivery_accepted", "policy_version")
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)
