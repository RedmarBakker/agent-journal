from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.loose_block import LooseBlock
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_blocked_on_another_is_taken_up_when_that_one_closes(story):
    header = story.agent_creates_task(story.agents.subject, "the header")
    story.agent_runs(story.agents.subject, f"task block {header} --on task:{story.tasks.started}")
    story.expect_task(header, state=TaskState.BLOCKED)
    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.started} --how done")
    story.expect_task(header, state=TaskState.STARTED)
    result.expect_agent_told(story.agents.subject, TasksNudges.TASK_REOPENED, n=header)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_blocked_by_hand_opens_when_unblocked(story):
    logo = story.agent_creates_task(story.agents.subject, "the logo")
    story.agent_runs(story.agents.subject, f"task block {logo} 'waits on the designer'")
    story.expect_task(logo, state=TaskState.BLOCKED)
    story.agent_runs(story.agents.subject, f"task unblock {logo}")
    story.expect_task(logo, state=TaskState.OPEN)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)



@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_waits_for_the_whole_plan_and_opens_when_it_finishes(story):
    release = story.agent_creates_task(story.agents.subject, "release after the plan")
    result = story.agent_runs(story.agents.subject, f"task block {release} --on plan:{story.plans.first}")
    result.expect_command_passed()
    story.expect_task(release, state=TaskState.BLOCKED, waits=[f"plans:{story.plans.first}"])
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how done")
    story.expect_task(release, state=TaskState.BLOCKED)
    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.second} --how done")
    story.expect_task(release, state=TaskState.STARTED, waits=[])
    result.expect_agent_told(story.agents.subject, TasksNudges.TASK_REOPENED, n=release)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_cancelled_plan_releases_the_task_waiting_on_it(story):
    release = story.agent_creates_task(story.agents.subject, "release if the plan ends")
    result = story.agent_runs(story.agents.subject, f"task block {release} --on plan:{story.plans.first}")
    result.expect_command_passed()
    story.user_cancels_plan(story.plans.first)
    story.expect_task(release, state=TaskState.STARTED, waits=[])
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_plan_does_not_release_a_task_with_another_open_wait(story):
    dependency = story.agent_creates_task(story.agents.subject, "another dependency")
    release = story.agent_creates_task(story.agents.subject, "release after both")
    result = story.agent_runs(story.agents.subject, f"task block {release} --on plan:{story.plans.first} --on task:{dependency}")
    result.expect_command_passed()
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how done")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.second} --how done")
    story.expect_task(release, state=TaskState.BLOCKED, waits=[f"tasks:{dependency}"])
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_wait_is_named_in_show_list_and_the_viewer_row(story):
    release = story.agent_creates_task(story.agents.subject, "release after the task")
    story.agent_runs(story.agents.subject, f"task block {release} --on task:{story.tasks.started}")
    result = story.agent_runs(story.agents.subject, f"task show {release}")
    result.expect_command_text(f"waiting on: task {story.tasks.started}")
    result = story.agent_runs(story.agents.subject, "task list")
    result.expect_command_text(f"release after the task  [waiting on: task {story.tasks.started}]")
    story.expect_task(release, waits=[f"tasks:{story.tasks.started}"])
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_wait_is_named_in_show_list_and_the_viewer_row(story):
    release = story.agent_creates_task(story.agents.subject, "release after the plan")
    result = story.agent_runs(story.agents.subject, f"task block {release} --on plan:{story.plans.first}")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"task show {release}")
    result.expect_command_text(f"waiting on: plan {story.plans.first}")
    result = story.agent_runs(story.agents.subject, "task list --all")
    result.expect_command_text(f"release after the plan  [waiting on: plan {story.plans.first}]")
    story.expect_task(release, waits=[f"plans:{story.plans.first}"])
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_started_task_itself_can_be_blocked_and_unblocking_takes_it_up_again(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'waits on the designer'").expect_command_passed()
    story.expect_task(story.tasks.started, state=TaskState.BLOCKED)
    story.agent_runs(story.agents.subject, f"task unblock {story.tasks.started}")
    story.expect_task(story.tasks.started, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_cannot_be_paused_any_more_and_is_pointed_to_block(story):
    result = story.agent_runs(story.agents.subject, f"task pause {story.tasks.started} 'later'")
    result.expect_command_refused()
    result.expect_command_text("task block")
    story.expect_stack(story.agents.subject, Ready, Working)


@story(LooseBlock, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_block_with_no_wait_is_named_every_five_completed_tasks_with_the_way_to_give_it_an_end(story):
    for title in ("one", "two", "three", "four"):
        task = story.agent_creates_task(story.agents.subject, title)
        result = story.agent_runs(story.agents.subject, f"task complete {task} --how done")
    result.expect_agent_told(story.agents.subject, TasksNudges.LOOSE_BLOCKS, n=story.tasks.loose)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_starting_another_task_blocks_the_one_in_hand_until_the_new_one_closes(story):
    header = story.agent_creates_task(story.agents.subject, "the header")
    result = story.agent_runs(story.agents.subject, f"task start {header}")
    result.expect_command_text(f"task {story.tasks.started} blocked until task {header} closes")
    story.expect_task(story.tasks.started, state=TaskState.BLOCKED, waits=[f"tasks:{header}"])
    story.agent_runs(story.agents.subject, f"task complete {header} --how done")
    story.expect_task(story.tasks.started, state=TaskState.STARTED, waits=[])
    story.expect_stack(story.agents.subject, Ready, Working)


@story(LooseBlock, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_block_with_no_wait_is_named_after_its_minutes_even_while_the_agent_is_idle(story):
    result = story.agent_is_quiet_past(story.agents.subject, story.setting(TasksOptions.LOOSE_BLOCK_MINUTES) * 60)
    result.expect_agent_told(story.agents.subject, TasksNudges.LOOSE_BLOCKS, n=story.tasks.loose)
    story.expect_stack(story.agents.subject, Ready)


@story(LooseBlock, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_block_with_no_wait_is_not_named_before_its_minutes_or_its_completed_tasks(story):
    result = story.agent_is_quiet_just_under(story.agents.subject, story.setting(TasksOptions.LOOSE_BLOCK_MINUTES) * 60)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.LOOSE_BLOCKS)
    story.expect_task(story.tasks.loose, state=TaskState.BLOCKED)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_block_that_waits_on_a_check_is_never_named_as_a_block_with_no_wait(story):
    logo = story.agent_creates_task(story.agents.subject, "the logo")
    story.agent_runs(story.agents.subject, f"task block {logo} --until false")
    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.started} --how done")
    for title in ("one", "two", "three", "four"):
        task = story.agent_creates_task(story.agents.subject, title)
        result = story.agent_runs(story.agents.subject, f"task complete {task} --how done")
    result.expect_agent_not_told(story.agents.subject, TasksNudges.LOOSE_BLOCKS)
    story.expect_stack(story.agents.subject, Ready)
