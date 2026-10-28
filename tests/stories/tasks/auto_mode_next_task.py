from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.plan_approved import PlanApproved
from tests.stories.fixtures.started_task import StartedTask
from tests.stories.fixtures.task_queue import TaskQueue
from tests.stories.fixtures.worker_delivered import WorkerDelivered
from tests.stories.fixtures.working_agent import WorkingAgent


@story(TaskQueue, end=[Ready, Working])
@setting(TasksOptions.AUTO, True)
def test_with_auto_on_a_completed_task_is_followed_by_the_next_open_one(story):
    story.agent_runs(f"task complete {story.start.started_task} --how done")
    story.expect_task(story.start.next_open, state=TaskState.STARTED)
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)


@story(TaskQueue, end=[Ready])
@setting(TasksOptions.AUTO, False)
def test_with_auto_off_a_completed_task_is_followed_by_nothing(story):
    story.agent_runs(f"task complete {story.start.started_task} --how done")
    story.expect_task(story.start.next_open, state=TaskState.OPEN)
    story.agent_stops()
    story.expect_allowed()


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.AUTO, True)
def test_the_next_task_is_the_one_of_highest_priority(story):
    low = story.agent_creates_task("the logo")
    high = story.agent_creates_task("the header")
    story.agent_runs(f"task edit {high} --priority critical")
    story.agent_runs(f"task complete {story.start.started_task} --how done")
    story.expect_task(high, state=TaskState.STARTED)
    story.expect_task(low, state=TaskState.OPEN)


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.AUTO, True)
def test_a_blocked_task_is_never_started(story):
    blocked = story.agent_creates_task("the logo")
    story.agent_runs(f"task block {blocked} 'waits on the designer'")
    header = story.agent_creates_task("the header")
    story.agent_runs(f"task complete {story.start.started_task} --how done")
    story.expect_task(blocked, state=TaskState.BLOCKED)
    story.expect_task(header, state=TaskState.STARTED)


@story(WorkerDelivered, end=[Ready])
@setting(TasksOptions.AUTO, True)
def test_a_task_a_worker_holds_is_never_started_by_the_stop(story):
    story.agent_stops()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task(story.start.briefed, state=TaskState.STARTED)


@story(PlanApproved, end=[Ready, FollowingPlan])
@setting(TasksOptions.AUTO, True)
def test_an_approved_plan_is_started_at_the_stop_with_its_first_task(story):
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)


@story(WorkingAgent, end=[Ready, Working])
@setting(TasksOptions.AUTO, True)
def test_a_stop_with_several_open_tasks_starts_only_one(story):
    first = story.agent_creates_task("the header")
    second = story.agent_creates_task("the logo")
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.expect_task(first, state=TaskState.STARTED)
    story.expect_task(second, state=TaskState.OPEN)
