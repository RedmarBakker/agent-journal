from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.leading_task import LeadingTask, LeadingTaskWorking
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.main.plans.plan_agent_reads_its_plan import prepare_plan_agent_worktrees


@story(NewSession, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_task_agent_reads_the_task_it_was_started_for(story, monkeypatch):
    prepare_plan_agent_worktrees(story, monkeypatch)
    task = story.agent_creates_briefed_task(story.agents.main, "outside task", "- the assigned task is visible")
    story.agent_runs(story.agents.main, f"task start {task}").expect_command_passed()

    session = "task-agent-task-reader"
    story.settle()
    story.session_starts_in(f"task-{task}", session).expect_allowed()
    read = story.agent_in_runs(story.agents.main, f"task-{task}", session, f"task show {task}")
    read.expect_command_passed()
    read.expect_command_text(f"task {task}: outside task")
    read.expect_command_text("the assigned task is visible")
    story.expect_stack(StoryAgent(AgentRole.MAIN, session=session), LeadingTask, LeadingTaskWorking)
