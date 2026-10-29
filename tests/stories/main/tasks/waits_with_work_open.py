from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, SOLO_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.mode_floor import ModeFloor
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.started_task import StartedTask

WAIT_MINUTES = 3
UNCOUNTED_SECONDS = 60
LONG_WAIT_MINUTES = 30
MEASURE_MINUTES = 1


@story(BuildWait, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.UNCOUNTED_WAIT_SECONDS, UNCOUNTED_SECONDS)
def test_a_wait_with_another_task_open_counts_the_seconds_past_the_first_ones(story):
    story.time_travel(minutes=WAIT_MINUTES)
    story.agent_reads(story.agents.subject)
    story.expect_seconds_waited_with_work_open(WAIT_MINUTES * 60 - UNCOUNTED_SECONDS)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.UNCOUNTED_WAIT_SECONDS, UNCOUNTED_SECONDS)
def test_a_wait_with_only_the_task_in_hand_counts_nothing(story):
    story.agent_runs(story.agents.subject, "await 'the build' --until false")
    story.time_travel(minutes=WAIT_MINUTES)
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_seconds_waited_with_work_open(0)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(BuildWait, mode=(BUILDER_MODE, SOLO_MODE), subject=AgentRole.MAIN)
@setting(FitnessOptions.WARNINGS, True)
def test_a_long_wait_with_another_task_open_names_the_next_work_at_the_next_tool_use(story):
    story.agent_is_quiet_for(story.agents.subject, minutes=MEASURE_MINUTES)
    story.time_travel(minutes=LONG_WAIT_MINUTES)
    story.agent_reads(story.agents.subject)
    story.agent_is_quiet_for(story.agents.subject, minutes=MEASURE_MINUTES)
    story.agent_reads(story.agents.subject)
    story.expect_agent_told(story.agents.subject, WorkersNudges.OPEN_WORK_WAIT_LINE, n=story.tasks.open)
    story.expect_stack(story.agents.subject, ModeFloor, Working)


@story(BuildWait, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(FitnessOptions.WARNINGS, True)
def test_an_orchestrators_long_wait_with_another_task_open_is_no_fitness_line(story):
    story.agent_is_quiet_for(story.agents.subject, minutes=MEASURE_MINUTES)
    story.time_travel(minutes=LONG_WAIT_MINUTES)
    story.agent_reads(story.agents.subject)
    story.agent_is_quiet_for(story.agents.subject, minutes=MEASURE_MINUTES)
    story.agent_reads(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.OPEN_WORK_WAIT_LINE)
    story.expect_stack(story.agents.subject, ModeFloor, Working)
