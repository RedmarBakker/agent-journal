from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.started_task import StartedTask
from tests.stories.fixtures.started_plan import StartedPlan
from tests.stories.fixtures.worker_delivered import WorkerDelivered


@story(StartedTask, end=[Ready])
def test_a_task_in_progress_moves_only_by_force_and_arrives_in_progress(story):
    second_environment = story.another_environment("second_environment")
    story.session_starts_in(second_environment, "s9")
    story.agent_runs(f"task transfer {story.start.started_task} {second_environment}")
    story.expect_command_refused()
    story.agent_runs(f"task transfer {story.start.started_task} {second_environment} --force")
    story.expect_command_passed()
    story.expect_task_in(second_environment, story.start.started_task, TaskState.STARTED)
    story.expect_task_not_in("main", story.start.started_task)
    story.expect_told_in(second_environment, TasksNudges.TASK_ARRIVED, n=story.start.started_task)
    story.agent_stops()
    story.expect_allowed()


@story(StartedTask, end=[Ready])
def test_a_task_in_progress_arrives_paused_where_a_task_is_already_in_progress(story):
    second_environment = story.another_environment("second_environment")
    theirs = story.agent_in_starts_task(second_environment, "s9", "Their own work")
    story.agent_runs(f"task transfer {story.start.started_task} {second_environment} --force")
    story.expect_task_in(second_environment, story.start.started_task, TaskState.PAUSED)
    story.expect_task_in(second_environment, theirs, TaskState.STARTED)


@story(StartedTask, end=[Ready])
def test_a_task_in_testing_moves_only_by_force_and_stays_in_testing(story):
    second_environment = story.another_environment("second_environment")
    story.agent_runs(f"task test {story.start.started_task}")
    story.agent_runs(f"task transfer {story.start.started_task} {second_environment}")
    story.expect_command_refused()
    story.agent_runs(f"task transfer {story.start.started_task} {second_environment} --force")
    story.expect_task_in(second_environment, story.start.started_task, TaskState.TESTING)


@story(StartedTask, end=[Ready, Working])
def test_a_paused_task_arrives_paused_and_is_no_longer_offered_here(story):
    second_environment = story.another_environment("second_environment")
    story.agent_runs(f"task pause {story.start.started_task} 'the second_environment environment takes it'")
    footer = story.agent_creates_task("Write the footer")
    story.agent_runs(f"task transfer {story.start.started_task} {second_environment}")
    story.expect_task_in(second_environment, story.start.started_task, TaskState.PAUSED)
    story.agent_stops()
    story.expect_agent_not_told(TasksNudges.PAUSED_CHOICE)
    story.expect_task(footer, state=TaskState.STARTED)


@story(StartedPlan, end=[Ready])
def test_a_plan_task_moves_only_by_force_and_the_plan_finishes_without_it(story):
    second_environment = story.another_environment("second_environment")
    story.agent_runs(f"task transfer {story.start.second_task} {second_environment}")
    story.expect_command_refused()
    story.agent_runs(f"task transfer {story.start.second_task} {second_environment} --force")
    story.agent_runs(f"task complete {story.start.first_task} --how done")
    story.expect_plan(story.start.plan, state=PlanState.FINISHED)
    story.expect_agent_told(PlansNudges.PLAN_FINISHED, n=story.start.plan)
    story.expect_task_in(second_environment, story.start.second_task, TaskState.OPEN)


@story(WorkerDelivered, end=[Ready])
def test_a_task_a_worker_holds_is_never_transferred(story):
    second_environment = story.another_environment("second_environment")
    story.agent_runs(f"task transfer {story.start.briefed} {second_environment} --force")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task_not_in(second_environment, story.start.briefed)
