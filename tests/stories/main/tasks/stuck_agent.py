from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.agent_impasse import AgentImpasse
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_stuck_with_tasks_open_lets_the_agent_stop_with_them_left_open(story):
    task = story.agent_creates_task(story.agents.subject, "the header")
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal stuck 'the build fails'")
    result.expect_allowed()
    result = story.agent_runs(story.agents.subject, "stuck 'the build fails'")
    result.expect_command_passed()
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Impasse)


@story(AgentImpasse, subject=AgentRole.MAIN)
def test_the_agents_next_tool_use_ends_the_stuck_state(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(AgentImpasse, subject=AgentRole.MAIN)
def test_a_journal_command_keeps_the_agent_stuck(story):
    story.agent_runs_in_the_shell(story.agents.subject, "journal task list")
    story.expect_stack(story.agents.subject, Ready, Impasse)


@story(AgentImpasse, subject=AgentRole.MAIN)
def test_the_users_prompt_ends_the_stuck_state(story):
    story.agent_is_prompted(story.agents.subject, "try the build again")
    story.expect_stack(story.agents.subject, Ready)


@story(AgentImpasse, subject=AgentRole.MAIN)
def test_a_stop_while_stuck_goes_through(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Impasse)


@story(StartedTask, subject=AgentRole.MAIN)
def test_an_agent_stuck_on_its_task_in_hand_waits_over_it_until_its_next_tool_use(story):
    story.agent_runs(story.agents.subject, "stuck 'the build fails on the footer'")
    story.expect_stack(story.agents.subject, Ready, Working, Impasse)
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_only_an_agent_says_it_is_stuck_and_the_user_typing_it_is_refused(story):
    result = story.user_types("stuck 'the build is red'")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
