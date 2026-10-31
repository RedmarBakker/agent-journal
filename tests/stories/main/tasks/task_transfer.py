from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_in_progress_moves_only_by_force_and_arrives_in_progress(story):
    second_environment = story.another_environment("second_environment")
    story.session_starts_in(second_environment, "s9")
    result = story.agent_runs(story.agents.subject, f"task transfer {story.tasks.started} {second_environment}")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"task transfer {story.tasks.started} {second_environment} --force")
    result.expect_command_passed()
    story.expect_task_in(second_environment, story.tasks.started, TaskState.STARTED)
    story.expect_task_not_in("main", story.tasks.started)
    story.expect_told_in(second_environment, TasksNudges.TASK_ARRIVED, n=story.tasks.started)
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_in_progress_arrives_blocked_where_a_task_is_already_in_progress(story):
    second_environment = story.another_environment("second_environment")
    theirs = story.agent_in_starts_task(story.agents.subject, second_environment, "s9", "Their own work")
    story.agent_runs(story.agents.subject, f"task transfer {story.tasks.started} {second_environment} --force")
    story.expect_task_in(second_environment, story.tasks.started, TaskState.BLOCKED)
    story.expect_task_in(second_environment, theirs, TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_in_testing_moves_only_by_force_and_stays_in_testing(story):
    second_environment = story.another_environment("second_environment")
    story.agent_runs(story.agents.subject, f"task test {story.tasks.started}")
    result = story.agent_runs(story.agents.subject, f"task transfer {story.tasks.started} {second_environment}")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"task transfer {story.tasks.started} {second_environment} --force")
    story.expect_task_in(second_environment, story.tasks.started, TaskState.TESTING)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_blocked_task_arrives_blocked_and_is_no_longer_offered_here(story):
    second_environment = story.another_environment("second_environment")
    story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'the second_environment environment takes it'")
    footer = story.agent_creates_task(story.agents.subject, "Write the footer")
    story.agent_runs(story.agents.subject, f"task transfer {story.tasks.started} {second_environment}")
    story.expect_task_in(second_environment, story.tasks.started, TaskState.BLOCKED)
    story.agent_stops(story.agents.subject)
    story.expect_task(footer, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_task_moves_only_by_force_and_the_plan_finishes_without_it(story):
    second_environment = story.another_environment("second_environment")
    result = story.agent_runs(story.agents.subject, f"task transfer {story.tasks.second} {second_environment}")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"task transfer {story.tasks.second} {second_environment} --force")
    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how done")
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    result.expect_agent_told(story.agents.subject, PlansNudges.PLAN_FINISHED, n=story.plans.first)
    story.expect_task_in(second_environment, story.tasks.second, TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_a_worker_holds_is_never_transferred(story):
    second_environment = story.another_environment("second_environment")
    result = story.agent_runs(story.agents.subject, f"task transfer {story.tasks.briefed} {second_environment} --force")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_task_not_in(second_environment, story.tasks.briefed)
    story.expect_stack(story.agents.subject, Ready)
